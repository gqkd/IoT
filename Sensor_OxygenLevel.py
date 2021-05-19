import time
import numpy as np
import threading
import requests
from MyMQTT import *

class SensorOxygen(threading.Thread):
    def __init__(self, deviceID, boxID, topic, publicURL):
        threading.Thread.__init__(self)
        self.deviceID = f"{boxID}{deviceID}"
        self.boxID = boxID
        self.topic = f"{topic}/{self.boxID}/{self.deviceID}/oxygen"  # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic,
            "Resource": "Oxygen",
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
                    'n': 'Oxygen Level',
                    'u': '%',
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
        #ossigenazione >=96% : tutto ok
        # 93% =< ossigenazione < 95% : possibili problemi
        # ossigenazione <92 % : ossigenazione insufficiente
        oxy_level = np.random.logistic(100, 0.6, 1).item()
        if oxy_level > 100:
            oxy_level = 100
        message = self.__message
        message['e'][0]['t'] = float(time.time())
        message['e'][0]['v'] = oxy_level
        self.client.myPublish(self.topic, message)
        print("\nMessage published by OxygenLevel Sensor")

    def stop_MyMQTT(self):
        self.client.stop()
