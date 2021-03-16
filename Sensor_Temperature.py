import numpy as np
import json
import time
import random
import threading
import requests
from MyMQTT import *

#TODO: i sensori devono essere a se stanti e registrarsi alla scatola 

class SensorTemperature(threading.Thread):
    def __init__(self, deviceID, boxID, topic):
        threading.Thread.__init__(self)
        self.deviceID = boxID+deviceID # ID deve essere numerico 
        self.boxID = boxID
        self.topic = topic # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic+"/"+ self.boxID +"/"+self.deviceID+"/temperature",
            "Resource": 'Temperature',
            "Timestamp": None
        }
        self.tempo1=6
        self.count = 0
            # "actuator": [
            #     {
            #     "Topic": self.topic+"/"+self.boxID+"/speaker",
            #     "Resource": 'Speaker',
            #     "Timestamp": None
            #     }

        
    def request(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(f"http://localhost:8070/Device", json=self.payload)
        print(r)
    
    def run(self):
        self.count += 1
        self.sendData()
        if self.count%self.tempo1 == 0: #tempo da impostare come parametro
            self.request()

    def sendData(self):
        print("1:publishing data")
        t = 100 #TODO simulazione output sensore 
        message = self.__message
        message['e'][0]['t'] = float(time.time())
        message['e'][0]['v'] = t
        self.client.myPublish(self.topic,message)   
        # time.sleep(10)
        print("2:run finished")

        
        
    def start_MyMQTT(self, broker, port):
        self.client = MyMQTT(self.deviceID, broker, port, None)
        self.__message={
            "bn": self.deviceID,
            "e": [
                    {
                        "n": "temperature",
                        "u": "Cel",
                        "t": None,
                        "v": ""
                    }
                ]
            }
        self.client.start()
    
    
        
    
    
    def stop_MyMQTT(self):
        self.client.stop()
        