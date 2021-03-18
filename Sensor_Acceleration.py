import time
import random
import threading
import requests
from MyMQTT import *

class SensorAcceleration(threading.Thread):
    def __init__(self, deviceID, boxID, topic):
        threading.Thread.__init__(self)
        #Definizione di: DeviceID, BoxID e topic
        #Topic nella forma: base_topic/numero_box/numero_box_numero_sensore/risorsa_misurata
        self.deviceID = f"{boxID}{deviceID}"
        self.boxID = boxID
        self.topic = f"{topic}/{self.boxID}/{self.deviceID}/acceleration"  # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic,
            "Resource": "Acceleration",
            "Timestamp": None
        }
        #Definizioni di configurazioni utili per il timing per sottoscrizione a catalog e per inviare dati dal sensore
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timesenddata = conf2["timesenddata"]
        self.timerequest = conf2["timerequest"]
        self.count = 6

    def start_MyMQTT(self, broker, port):
        self.client = MyMQTT(self.deviceID, broker, port, None)
        self.__message = {
            "bn": self.deviceID,
            "e": [
                {
                    "n": "acceleration",
                    "u": "m/s^2",
                    "t": None,
                    "v_xaxis": "",      #accelerometri misurano accelerazione in tutte e tre le direzioni spaziali
                    "v_yaxis":"",       #sarebbe conveniente spezzare il sensore in tre sottosensori ma viene fuori un casino
                    "v_zaxis":""
                }
            ]
        }
        self.client.start()

    def request(self):
        self.payload["Timestamp"] = time.time()
        #Mantengo URL inserito da Giulio
        r = requests.put(f"https://boxcatalog.loca.lt/Device", json=self.payload)
        print(r)

    def run(self):
        while True:
            self.sendData()
            if self.count % self.timerequest == 0:
                self.request()
                self.count = 0
            self.count += 1
            time.sleep(self.timesenddata)

    def sendData(self):
        message = self.__message
        message['e'][0]['t'] = float(time.time())
        #distribuzione uniforme per accelerazione
        message['e'][0]['v_xaxis'] = random.uniform(0.1, 0.5)
        message['e'][0]['v_yaxis'] = random.uniform(0.1, 0.5)
        message['e'][0]['v_zaxis'] = random.uniform(0.1, 0.5)
        self.client.myPublish(self.topic, message)

    def stop_MyMQTT(self):
        self.client.stop()
