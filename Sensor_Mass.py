import time
import random
import threading
import requests
from MyMQTT import *

class SensorMass(threading.Thread):
    def __init__(self, deviceID, boxID, topic, publicURL):
        threading.Thread.__init__(self)
        self.deviceID = f"{boxID}{deviceID}"
        self.boxID = boxID
        self.topic = f"{topic}/{self.boxID}/{self.deviceID}/mass"  # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic,
            "Resource": "Mass",
            "Timestamp": None
        }
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timesenddata = conf2["timesenddata"]
        self.timerequest = conf2["timerequest"]
        self.count = 6
        self.url=publicURL

    def start_MyMQTT(self, broker, port):
        self.client = MyMQTT(self.deviceID, broker, port, None)
        self.__message = {
            'bn': self.deviceID,
            'e': [
                {
                    'n': 'mass',
                    'u': 'kg',
                    't': None,
                    'v': None
                }
            ]
        }
        self.client.start()

    def request(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(self.url+"/Device", json=self.payload)
        print(f"\n{self.deviceID} registered to Box Catalog with result {r.status_code}")

    def run(self):
        while True:
            self.sendData()
            if self.count % (self.timerequest/self.timesenddata) == 0:
                self.request()
                self.count = 0
            self.count += 1
            time.sleep(self.timesenddata)

    def sendData(self):
        #Mi aspetto che il peso dell'organo sia fisso e non vari con il tempo
        #ex. cuore umano di un adulto maschio arriva fino a 300 g mentre quello di una donna adulta fino a 150/200g
        #scatola sarà comunque settata in qualche modo affinchè riproduca stessa misura
        peso = 0.1
        message = self.__message
        message['e'][0]['t'] = float(time.time())
        message['e'][0]['v'] = peso
        self.client.myPublish(self.topic, message)
        print("\nMessage published by Weight Sensor")

    def stop_MyMQTT(self):
        self.client.stop()
