import numpy as np
import json
import time
import random
import threading
import requests
from progetto.MyMQTT import *

class Led(threading.Thread):
    def __init__(self, sensorID, topic):
        threading.Thread.__init__(self)
        self.sensorID = sensorID
         
        self.topic = topic
        self.payload = {
            "DeviceID": self.sensorID, 
            "Topic": self.topic,
            "Resource": 'Led',
            "Timestamp": None
            }
        
        
    
    def run(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(f"http://localhost:8070/Device", json=self.payload)
        print(r)
        time.sleep(10)
        
    def start_MyMQTT(self, broker, port):
        self.client = MyMQTT(self.sensorID, broker, port, None)
        self.client.start()
    
    def sendData(self):
        self.client.myPublish(self.topic,message)   
        time.sleep(2)
    
    
    def stop_MyMQTT(self):
        self.client.stop()
        
        
if __name__ == '__main__':
    conf=json.load(open("settings.json"))
    senorsID = "Publisher_Led_Bonfanti"
    topic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]
    
    # thread_mqtt = Led(senorsID, topic)
    
    
    # thread_mqtt.start_MyMQTT(broker, port)
    time.sleep(1)
    
    
    while True:
        try:
            # thread_mqtt.sendData()
            thread_rest = Led(senorsID, topic)
            thread_rest.start()
            thread_rest.join()
            
        except KeyboardInterrupt:
            # thread_mqtt.stop_MyMQTT()
            break
            