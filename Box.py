import numpy as np
import json
import time
import random
import threading
import requests
import sys
from MyMQTT import *
       
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
            