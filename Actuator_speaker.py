import time
import threading
import requests
from MyMQTT import *
# "actuator": [
            #     {
            #     "Topic": self.topic+"/"+self.boxID+"/speaker",
            #     "Resource": 'Speaker',
            #     "Timestamp": None
            #     }
class Speaker(threading.Thread):
    def __init__(self, speakerID, boxID, topic):
        threading.Thread.__init__(self)
        self.speakerID = f"{boxID}{speakerID}"  # ID deve essere numerico
        self.boxID = boxID
        # ACCENSIONE/SPEGNIMENTO SPEAKER è SINGOLO PER OGNI BOX CRISTO
        self.topic = f"{topic}/{self.boxID}/{self.speakerID}/speaker"  # self.topic= "Ipfsod"
        self.payload = {
            "deviceID": self.speakerID,
            "Topic": self.topic,
            "Resource":'Boolean',
            "Timestamp": None
        }

    def start_MyMQTT(self, broker, port):
        # SPEAKER è UN SUBSCRIBER
        self.client = MyMQTT(self.speakerID, broker, port, self)
        self.client.start()
        self.client.mySubscribe(self.topic)

    def request(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(f"http://127.0.0.1:8070/Device", json=self.payload)
        print(r)


    
    def stop_MyMQTT(self):
        self.client.stop()