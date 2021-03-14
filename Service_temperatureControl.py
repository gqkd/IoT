import json
import time
import requests
import sys
from MyMQTT import *

class TemperatureControl():
    def __init__(self, serviceID):
        self.serviceID = serviceID
        self.payload = {
            "serviceID": self.serviceID, 
            "Topic": self.topic+"/"+self.serviceID+"/temperatureControl"
            }
 
        
    def start_MyMQTT(self, broker, port, topic):

        self.client = MyMQTT(self.serviceID, broker, port, self)
        
        self.client.start()
        self.client.mySubscribe(self.topic)
        print('{} has started'.format(self.serviceID))    
    
    def topicRequest(self):
        self.payload["Timestamp"] = time.time()
        r = requests.put(f"http://localhost:8070/Service", json=self.payload) # Sottoscrizione al Catalog

    
    def topicRequest(self):
        r = requests.get("http://localhost:8070/GetTemperature") # Richiesta GET per topic
        jsonBody = json.loads(r.content)
        self.topicList = jsonBody["topics"]
        
    
    def stop_MyMQTT(self):
        self.client.stop()
        print('{} has stopped'.format(self.serviceID))
        
    def notify(self,topic,msg):
        payload=json.loads(msg)
        if payload['e'][0]['v'] > 110:
            print("   !!!   DANGER! HIGH FREQUENCY   !!!")
        print(json.dumps(payload,indent=4))
        
    def sendData(self):
        #Pubblica info sulla temperatura di tutte le Box
        pass



if __name__ == '__main__':
    conf=json.load(open("settings1.json"))
    serviceID = "Subscriver_sensHeartRate_Bonfanti"
    broker = conf["broker"]
    port = conf["port"]
    
    TC = TemperatureControl(serviceID)
    while True:
        topicList = TC.topicrequest()
        for topicList:
            
        
    
    
    heartRate.start_MyMQTT(broker,port)
    
    choice = ''
    while choice!='q':
        choice=input("'q' to quit\n")

    heartRate.stop_MyMQTT()