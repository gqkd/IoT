import time
import random
import threading
import requests
from MyMQTT import *

class SensorTemperature(threading.Thread):
    def __init__(self, deviceID, boxID, topic, publicURL):
        threading.Thread.__init__(self)
        self.deviceID = f"{boxID}{deviceID}" # ID deve essere numerico 
        self.boxID = boxID
        self.topic = f"{topic}/{self.boxID}/{self.deviceID}/temperature" # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic,
            "Resource": "Temperature",
            "Timestamp": None
        }
        #Dati utili per timing
        conf2=json.load(open("settingsboxcatalog.json"))
        self.timesenddata = conf2["timesenddata"]
        self.timerequest=conf2["timerequest"]
        self.count = 6
        self.url=publicURL

    def start_MyMQTT(self, broker, port):
        self.client = MyMQTT(self.deviceID, broker, port, None)
        self.__message={
            'bn': self.deviceID,
            'e': [
                    {
                        'n': 'temperature',
                        'u': 'Cel',
                        't': None,
                        'v': None
                    }
                ]
            }
        self.client.start()

    def request(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(self.url+"/Device", json=self.payload)
        print(f"{self.deviceID} registrato al box con risultato {r.status_code}")
    
    def run(self):
        while True:
            self.sendData()
            if self.count % (self.timerequest/self.timesenddata) == 0:
                self.request()
                self.count=0
            self.count += 1
            time.sleep(self.timesenddata)

    def sendData(self):
        message = self.__message
        message['e'][0]['t'] = float(time.time())
        message['e'][0]['v'] = random.randrange(34,39)
        self.client.myPublish(self.topic,message)

    def stop_MyMQTT(self):
        self.client.stop()
        