import json
import time
import requests
import sys
from MyMQTT3 import *

class HRControl():
    def __init__(self, serviceID):
        self.serviceID = serviceID
         
        
    def start_MyMQTT(self,broker, port):
        #richiesta GET per topic
        r = requests.get("http://localhost:8070/GetDevice?ID=Publisher_sensHeartRate_Bonfanti")
        jsonBody = json.loads(r.content)
        self.topic = jsonBody["Topic"]
        
        self.client = MyMQTT(self.serviceID, broker, port, self)
        self.client.start()
        self.client.mySubscribe(self.topic)
        print('{} has started'.format(self.serviceID))    
    
    def stop_MyMQTT(self):
        self.client.stop()
        print('{} has stopped'.format(self.serviceID))
        
    def notify(self,topic,msg):
        payload=json.loads(msg)
        if payload['e'][0]['v'] > 110:
            print("   !!!   DANGER! HIGH FREQUENCY   !!!")
        print(json.dumps(payload,indent=4))

        
        
        




if __name__ == '__main__':
    conf=json.load(open("settings1.json"))
    serviceID = "Subscriver_sensHeartRate_Bonfanti"
    broker = conf["broker"]
    port = conf["port"]
    
    heartRate = HRControl(serviceID)
    heartRate.start_MyMQTT(broker,port)
    
    choice = ''
    while choice!='q':
        choice=input("'q' to quit\n")

    heartRate.stop_MyMQTT()