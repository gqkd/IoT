import numpy as np
import json
import time
import random
import threading
import requests
from Sensor_Temperature import *
       
if __name__ == '__main__':
    conf=json.load(open("settings.json"))
    conf2=json.load(open("settingsboxcatalog.json"))
    timesenddata = conf2["timesenddata"]
    topic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]
    
    temp1 = SensorTemperature("100", "001", topic)
    temp2 = SensorTemperature("100", "002", topic)
    # press = SensorPressure("200", "001", topic)
    
    temp1.start_MyMQTT(broker, port)
    temp2.start_MyMQTT(broker, port)
    # press.start_MyMQTT(broker, port)
    temp1.start()
    temp2.start()

    # temp1.stop_MyMQTT()