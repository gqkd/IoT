import time
import threading
import json
import requests
from MyMQTT import *
class Speaker(threading.Thread):
    def __init__(self, speakerID, boxID, broker, port):
        threading.Thread.__init__(self)
        self.speakerID = f"{boxID}{speakerID}"  # ID deve essere numerico
        self.boxID = boxID
        self.broker = broker
        self.port = port
        self.mode = 0
        self.payload = {
            "deviceID": self.speakerID,
            "Resource":'Boolean',
            "Timestamp": None
        }

    def request(self):
        # Sottoscrizione al boxcatalog
        self.payload["Timestamp"] = time.time()
        requests.put(f"http://localhost:8070/Device", json=self.payload)  # Sottoscrizione al Catalog

    def topicRequest(self):
        # Richiesta GET per topic del servizio
        r = requests.get("http://localhost:8070/GetTopicTemperature")
        jsonBody = json.loads(r.content)
        listatopicService = jsonBody["topics"]
        # Una volta ottenuto il topic, subscriber si sottoscrive a questo topic per ricevere dati
        self.client = MyMQTT(self.speakerID, self.broker, self.port, self)
        self.client.start()
        for topic in listatopicService:
            self.client.mySubscribe(topic)  # TOPIC RICHIESTO A CATALOG
            print('{} has started'.format(self.speakerID))

    def notify(self,topic,msg):
        messaggio = json.loads(msg)
        listachiavi = list(messaggio.keys())
        deviceID = messaggio['DeviceID']
        d = {'Temperature':None, 'Acceleration':None,'Oxygen':None}
        if self.boxID == deviceID[0:3]:
            if 'Temperature' in listachiavi:
                val = messaggio['Temperature']
                d['Temperature'] = val
            elif 'Acceleration' in listachiavi:
                val = messaggio['Acceleration']
                d['Acceleration']=val
            elif 'Oxygen' in listachiavi:
                val = messaggio['Oxygen']
                d['Oxygen']=val
            listavalori= list(d.values())
            if sum(listavalori) > 0:
                self.mode = 1
                print('A T T E N Z I O N E: \n ALLARME ATTIVO')
            else:
                self.mode = 0

    def stop_MyMQTT(self):
        self.client.stop()