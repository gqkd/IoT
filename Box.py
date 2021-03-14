import numpy as np
import json
import time
import random
import threading
import requests
import sys
from MyMQTT import *

#TODO: i sensori devono essere a se stanti e registrarsi alla scatola 

class HeartRateSensor(threading.Thread):
    def __init__(self, boxID, topic):
        threading.Thread.__init__(self)
        self.boxID = boxID
         
        self.topic = topic # self.topic= "Ipfsod"
        self.payload = {
            "boxID": self.boxID, 
            "sensors": [
                {
                "Topic": self.topic+"/"+self.boxID+"/temperature",
                "Resource": 'Temperature',
                "Timestamp": None
                },
                {
                "Topic": self.topic+"/"+self.boxID+"/accelerometer",
                "Resource": 'Acceleration',
                "Timestamp": None
                },
                {
                "Topic": self.topic+"/"+self.boxID+"/weight",
                "Resource": 'Weight',
                "Timestamp": None
                },
                {
                "Topic": self.topic+"/"+self.boxID+"/GPS",
                "Resource": 'Position',
                "Timestamp": None
                }
            ],
            "actuator": [
                {
                "Topic": self.topic+"/"+self.boxID+"/speaker",
                "Resource": 'Speaker',
                "Timestamp": None
                }
            ]
            }
        
        
    
    def run(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(f"http://localhost:8070/Box", json=self.payload)
        print(r)
        time.sleep(10)
        
        
        #TODO SENSORI 
    def start_MyMQTT(self, broker, port):
        self.client = MyMQTT(self.sensorID, broker, port, None)
        self.__message={
            "bn": self.sensorID,
            "e": [
                    {
                        "n": "heart rate",
                        "u": "bpm",
                        "t": "",
                        "v": ""
                    }
                ]
            }
        self.client.start()
    
    def sendData(self):
        shape, scale = 2., 2.  # mean=4, std=2*sqrt(2)
        lista = 8*np.random.gamma(shape, scale, 1)+55
        hr = round(lista[0])
        message = self.__message
        message['e'][0]['t'] = str(time.time())
        message['e'][0]['v'] = hr
        self.client.myPublish(self.topic,message)   
        time.sleep(2)
    
    
    def stop_MyMQTT(self):
        self.client.stop()
        
        
if __name__ == '__main__':
    conf=json.load(open("settings.json"))
    senorsID = "Publisher_sensHeartRate_Bonfanti2"
    topic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]
    
    thread_mqtt = HeartRateSensor(senorsID, topic)
    
    
    thread_mqtt.start_MyMQTT(broker, port)
    time.sleep(1)
    
    
    while True:
        # try:
            thread_mqtt.sendData()
            thread_rest = HeartRateSensor(senorsID, topic)
            thread_rest.start()
            thread_rest.join()
            
        # except KeyboardInterrupt:
        #     thread_mqtt.stop_MyMQTT()
        #     break
            