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
        self.client = MyMQTT(self.speakerID, self.broker, self.port, self)
        # FORSE NON è MEGLIO FARE TRE SUBSCRIBER DIVERSI CHE SI SOTTOSCRIVONO SEPARATAMENTE ALLA COSA?
        # ROBA NON è SINCRONA
        # self.client1 = MyMQTT(self.speakerID, self.broker, self.port, self)
        # self.client2 = MyMQTT(self.speakerID, self.broker, self.port, self)
        self.client.start()
        # self.client1.start()
        # self.client2.start()
        # self.client.mySubscribe(listatopicService[0])
        # self.client1.mySubscribe(listatopicService[1])
        #self.client2.mySubscribe(listatopicService[2])
        for topic in listatopicService:
        # self.client.unsubscribe()
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
        # TODO: SE C'è SERVIZIO DEL PESO, ALLORA ATTIVA TUTTI GLI ALTRI SERVIZI
        self.d = {'Temperature': 0, 'Acceleration': 0, 'Oxygen': 0, 'Mass':0}
        if self.boxID == deviceID[0:3]:
            print(f"""Messaggio ricevuto da attuatore: {messaggio}""")
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
