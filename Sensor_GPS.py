import time
import random
import numpy as np
import threading
import requests
from MyMQTT import *

class SensorGPS(threading.Thread):
    def __init__(self, deviceID, boxID, topic, publicURL):
        threading.Thread.__init__(self)
        file = json.load(open("GPSsimulator.json"))
        self.coordinate = file["Coordinates"]
        self.deviceID = f"{boxID}{deviceID}" # ID deve essere numerico 
        self.boxID = boxID
        self.topic = f"{topic}/{self.boxID}/{self.deviceID}/GPS" # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic,
            "Resource": "GPS",
            "Timestamp": None
        }
        #Dati utili per timing
        conf2=json.load(open("settingsboxcatalog.json"))
        self.timesenddata = conf2["timesenddata"]
        self.timerequest=conf2["timerequest"]
        self.count = 6
        self.url=publicURL
        self.cont = 0

    def start_MyMQTT(self, broker, port):
        self.client = MyMQTT(self.deviceID, broker, port, None)
        self.__message={
            'bn': self.deviceID,
            'e': [
                    {
                        'n': 'GPS',
                        'u': 'DD',
                        't': None,
                        'v_lat': None,
                        'v_lon': None,
                        'v_time': None
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
        if self.cont >= 2060:
            self.cont=2060
        message['e'][0]['t'] = float(time.time())   
        message['e'][0]['v_lon'] = self.coordinate[self.cont]["lon"]
        message['e'][0]['v_lat'] = self.coordinate[self.cont]["lat"]
        message['e'][0]['v_time'] = np.round(120-self.cont/4*30/60) #120 perchè è la durata del viaggio simulato in minuti. a cui sottrggo il tempo passato preso dal cont
        self.cont += 4
        self.client.myPublish(self.topic,message)

    def stop_MyMQTT(self):
        self.client.stop()
        