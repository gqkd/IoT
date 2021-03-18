import time
import random
import threading
import requests
from MyMQTT import *

class SensorAccelerometer(threading.Thread):
    def __init__(self, deviceID, boxID, topic):
        threading.Thread.__init__(self)
        #Definizione di: DeviceID, BoxID e topic
        #Topic nella forma: base_topic/numero_box/numero_box_numero_sensore/risorsa_misurata
        self.deviceID = f"{boxID}{deviceID}"
        self.boxID = boxID
        self.topic = f"{topic}/{self.boxID}/{self.deviceID}/weight"  # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic,
            "Resource": "Weigth",
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
                    "n": "weight",
                    "u": "kg",
                    "t": None,
                    "v": ""
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
        #Mi aspetto che il peso dell'organo sia fisso e non vari con il tempo
        peso = 0.2
        message = self.__message
        message['e'][0]['t'] = float(time.time())
        message['e'][0]['v'] = peso
        self.client.myPublish(self.topic, message)

    def stop_MyMQTT(self):
        self.client.stop()
