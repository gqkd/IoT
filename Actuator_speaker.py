import time
import threading
import requests
from MyMQTT import *


class Speaker(threading.Thread):
    def __init__(self, speakerID, boxID, broker, port, publicURL):
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
        self.client = MyMQTT(self.speakerID, self.broker, self.port, self)
        self.client.start()
        # Dati utili per timing
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timerequestTopic = conf2["timerequestTopic"]
        self.timerequest = conf2["timerequest"]
        self.count = 6
        self.url = publicURL

    def request(self):
        # Sottoscrizione al boxcatalog
        self.payload["Timestamp"] = time.time()
        requests.put(self.url+"/Device", json=self.payload)  # Sottoscrizione al Catalog

    def topicRequest(self):
        # Richiesta GET per topic del servizio
        r = requests.get(self.url+"/GetTopic")
        jsonBody = json.loads(r.content)
        listatopicService = jsonBody["topics"]
        # Una volta ottenuto il topic, subscriber si sottoscrive a questo topic per ricevere dati
        #self.client = MyMQTT(self.speakerID, self.broker, self.port, self)
        #self.client.stop()
        #self.client.start()
        for topic in listatopicService:
            self.client.mySubscribe(topic)  # TOPIC RICHIESTO A CATALOG
       
        
    def run(self):
        while True:
            self.topicRequest()
            if self.count % (self.timerequest/self.timerequestTopic) == 0:
                self.request()
                self.count=0
            self.count += 1
            time.sleep(self.timerequestTopic)

    def notify(self, topic, msg):
        messaggio = json.loads(msg)
        listachiavi = list(messaggio.keys())
        deviceID = messaggio['DeviceID']
        self.d = {'Temperature': 0, 'Acceleration': 0, 'Oxygen': 0, 'Mass': 0}
        f =1
        # QUESTA COSA NON PUò FUNZIONARE
        if 'Mass' in listachiavi and messaggio['Mass'] == 0:
            f = 1
            self.d['Mass'] =0
        if f == 1 and self.boxID == deviceID[0:3]:
            print(f"""MESSAGGIO RICEVUTO DA ATTUATOREEEEEEEEE:\n {messaggio}""")
            if 'Temperature' in listachiavi:
                self.d['Temperature'] = messaggio['Temperature']
            elif 'Acceleration' in listachiavi:
                self.d['Acceleration'] = messaggio['Acceleration']
            elif 'Oxygen' in listachiavi:
                self.d['Oxygen'] = messaggio['Oxygen']

        if sum(list(self.d.values())) > 0:
            print('A T T E N Z I O N E: \n ALLARME ATTIVO')
        else:
            pass

    def stop_MyMQTT(self):
        self.client.stop()
