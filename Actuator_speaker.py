import time
import threading
import requests
from MyMQTT import *


class Speaker(threading.Thread):
    def __init__(self, speakerID, boxID, broker, port):
        threading.Thread.__init__(self)
        self.speakerID = f"{boxID}{speakerID}"  # ID deve essere numerico
        self.boxID = boxID
        self.broker = broker
        self.port = port
        self.payload = {
            "deviceID": self.speakerID,
            "Resource": 'Speaker',
            "Timestamp": None
        }
        # Dati utili per timing
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timesenddata = conf2["timesenddata"]
        self.timerequest = conf2["timerequest"]
        self.count = 6

    def request(self):
        # Sottoscrizione al boxcatalog
        self.payload["Timestamp"] = time.time()
        requests.put(f"http://localhost:8070/Device", json=self.payload)  # Sottoscrizione al Catalog

    def topicRequest(self):
        # Richiesta GET per topic del servizio
        r = requests.get("http://localhost:8070/GetTopic")
        jsonBody = json.loads(r.content)
        listatopicService = jsonBody["topics"]
        # Una volta ottenuto il topic, subscriber si sottoscrive a questo topic per ricevere dati
        self.client = MyMQTT(self.speakerID, self.broker, self.port, self)
        self.client.start()
        #for topic in listatopicService:
        self.client.mySubscribe("Ipfsod/+/temperatureControl")  # TOPIC RICHIESTO A CATALOG

    def run(self):
        self.request()
        while True:
            self.topicRequest()
            if self.count % self.timerequest == 0:
                self.request()
                self.count=0
            self.count += 1
            time.sleep(self.timesenddata)

    def notify(self, topic, msg):
        messaggio = json.loads(msg)
        print(f"""Messaggio ricevuto da attuatore: {messaggio}""")
        listachiavi = list(messaggio.keys())
        deviceID = messaggio['DeviceID']
        d = {'Temperature': None, 'Acceleration': 0, 'Oxygen': 0}
        if self.boxID == deviceID[0:3]:
            if 'Temperature' in listachiavi:
                d['Temperature'] = messaggio['Temperature']
            elif 'Acceleration' in listachiavi:
                d['Acceleration'] = messaggio['Acceleration']
            elif 'Oxygen' in listachiavi:
                d['Oxygen'] = messaggio['Oxygen']
            listavalori = list(d.values())
            if sum(listavalori) > 0:
                print('A T T E N Z I O N E: \n ALLARME ATTIVO')
            else:
                pass

    def stop_MyMQTT(self):
        self.client.stop()
