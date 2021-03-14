import numpy as np
import json
import time
import random
import threading
import requests
import sys
from MyMQTT import *

#TODO: i sensori devono essere a se stanti e registrarsi alla scatola 

class SensorTemperature(threading.Thread):
    def __init__(self, deviceID, boxID, topic):
        threading.Thread.__init__(self)
        self.deviceID = deviceID # ID deve essere numerico 
        self.boxID = boxID
        self.topic = topic # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.deviceID,
            "Topic": self.topic+"/"+ self.boxID +"/"+self.deviceID+"/temperature",
            "Resource": 'Temperature',
            "Timestamp": None
        }
                
            # "actuator": [
            #     {
            #     "Topic": self.topic+"/"+self.boxID+"/speaker",
            #     "Resource": 'Speaker',
            #     "Timestamp": None
            #     }

        
        
    
    def run(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(f"http://localhost:8070/Device", json=self.payload)
        print(r)
        time.sleep(10)
        
        
        #TODO SENSORI 
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
    
    def sendData(self):
        t = random.randint(1,10) #TODO simulazione output sensore 
        message = self.__message
        message['e'][0]['t'] = float(time.time())
        message['e'][0]['v'] = t
        self.client.myPublish(self.topic,message)   
        time.sleep(2)
    
    
    def stop_MyMQTT(self):
        self.client.stop()
        