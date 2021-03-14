import numpy as np
import json
import time
import random
import threading
import requests
from Sensor_Temperature import *
       
if __name__ == '__main__':
    conf=json.load(open("settings.json"))
    
    
    topic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]
    
    temp1 = SensorTemperature("100", "001", topic)
    # press = SensorPressure("200", "001", topic)
    
    temp1.start_MyMQTT(broker, port)
    # press.start_MyMQTT(broker, port)
    
    time.sleep(1)
    
    
    while True:
        temp1.sendData()
        temp = SensorTemperature("100", "001", topic)      
        temp.start()
        temp.join()
        print("3:thread finished")
        # press.start()
        # time.sleep(10)
        
    temp1.stop_MyMQTT()