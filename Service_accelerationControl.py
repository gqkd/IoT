import time
import threading
import requests
from math import sqrt
from MyMQTT import *


# NOTE BEA: SERVIZIO DEVE CONNETTERSI IN LOOP A BOX CATALOG E DEVE CONTINUARE A CHIEDERE A BOX CATALOG TOPIC
# DELLA TEMPERATURA. UNA VOLTA OTTENUTO, DEVE FARE TUTTA LA SUA MANFRINA DEL CONTROLLO
# QUINDI, WORKFLOW:
# - SOTTOSCRIVERSI IN LOOP A BOX CATALOG
# - CHIEDERE IN LOOP TOPIC DEI SENSORI CHE PUBBLICANO TEMPERATURA
# - SOLO DOPO AVER RICEVUTO IL TOPIC, POSSO FARE TEMPERATURE CONTROL

class AccelerationControl(threading.Thread):
    def __init__(self, serviceID, topic, broker, port, publicURL):
        threading.Thread.__init__(self)
        self.serviceID = serviceID
        self.topic = topic  # basetopic
        self.topicresource = '' # topic che verrà chiesto a box catalog
        self.broker = broker
        self.port = port
        self.payload = {
            "serviceID": self.serviceID,
            "Topic": f"""{self.topic}/{self.serviceID}/accelerationControl""""",
            "Resource": "Service",
            "Timestamp": None
        }
        # Dati utili per il timing
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timerequestTopic = conf2["timerequestTopic"]
        self.timerequest = conf2["timerequest"]
        self.count = 6
        self.url=publicURL

    def request(self):
        # Sottoscrizione al boxcatalog
        self.payload["Timestamp"] = time.time()
        requests.put(self.url+"/Service", json=self.payload)  # Sottoscrizione al Catalog

    def topicRequest(self):
        
        # Richiesta GET per topic
        r = requests.get(self.url+"/GetAcceleration")
        jsonBody = json.loads(r.content)
        self.topicresource = jsonBody["topics"]
        # Una volta ottenuto il topic, subscriber si sottoscrive a questo topic per ricevere dati
        self.client = MyMQTT(self.serviceID, self.broker, self.port, self)
        self.client.stop()
        self.client.start()
        #self.client.unsubscribe()
        self.client.mySubscribe(self.topicresource)  # TOPIC RICHIESTO A CATALOG


    def run(self):
        while True:
            self.topicRequest()
            if self.count % (self.timerequest/self.timerequestTopic) == 0:
                self.request()
                self.count=0
            self.count += 1
            time.sleep(self.timerequestTopic)
            
            
    def notify(self, topic, msg):
        payload = json.loads(msg)
        print(f"Messaggio ricevuto da servizio: {payload}")
        # Estrazione dei valori di accelerazione su ogni asse
        ax = payload['e'][0]["v_xaxis"]
        ay = payload['e'][0]["v_yaxis"]
        az = payload['e'][0]["v_zaxis"]
        # Calcolo dell'accelerazione complessiva
        a_tot = sqrt(ax**2+ay**2+az**2)
        # Avvisare speaker e mandare dato a thingspeak
        if a_tot> 0.5:
            messaggio = {'Acceleration':1, "DeviceID": payload['bn']}       # CODICE PER DIRE CHE ACCELERAZIONE NON VA BENE
        else:
            messaggio = {'Acceleration': 0, "DeviceID":payload['bn']}      # CODICE PER DIRE CHE ACCELERAZIONE VA BENE
        self.client.myPublish(f"{self.topic}/{self.serviceID}/accelerationControl", messaggio)

    def stop_MyMQTT(self):
        self.client.stop()
        print('{} has stopped'.format(self.serviceID))

