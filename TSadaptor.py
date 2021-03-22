#TS adaptor:
# 1. chiede al box catalog dove si deve iscrivere per i topic dei sensori -> ricorsivo ogni tot sec
# 2. si iscrive ai topic in questione
# 3. manda una request HTTP a thingspeak per cercare se c'è il canale della box
# 4. se non c'è crea il canale per la box in questione
# 5. spedisce i dati in HTTP a thingspeak
from MyMQTT import *
import time
import requests
import json

class TSadaptor:
    def __init__(self,broker,port,apikey): #unica cosa che serve per certo è l'indirizzo del box catalog
        r = requests.get("https://api.thingspeak.com/channels/1333953/fields/1.json?api_key=12YLI1DSAWUJS27X&results=1")
        jsonBody=json.loads(r.text)
        self.url=jsonBody['feeds'][0]['field1']
        self.serviceID = "TSadaptor"
        self.broker = broker
        self.port = port
        self.api = apikey
        self.client = MyMQTT(self.serviceID, self.broker, self.port, self)
        self.client.start()

    def topicsearch(self):
        r=requests.get(self.url+"/Dumpitallmodafaccar")
        jsonBody = json.loads(r.content)
        listatopicServices = jsonBody["services"]
        listatopicDevices = jsonBody["devices"]
        
        for t1 in range(len(listatopicServices)):
            self.client.mySubscribe(listatopicServices[t1]['Topic']) 
        for t2 in range(len(listatopicDevices)):
            if listatopicDevices[t2]['Resource']!='Speaker':
                self.client.mySubscribe(listatopicDevices[t2]['Topic'])
        # self.client.mySubscribe("Giulio1234567890")

    def notify(self, topic, msg):
        payload = json.loads(msg)
        print(f"Messaggio ricevuto da servizio: {payload}")


    def run(self):
        while True:
            self.topicsearch()
            time.sleep(30)

    def createnewchannel(self, nome_canale):
        payload={
            'api_key':self.api,
            'field1':"Health",
            'field2':"Acceleration",
            'field3':"OxygenLevel",
            'field4':"Temperature",
            'field5':"Acc_control",
            'field6':"Oxy_control",
            'field7':"Temp_control",
            'name':nome_canale,
            'public_flag':True,
        }
        r = requests.post("https://api.thingspeak.com/channels.json",json=payload)
        jsonBody = json.loads(r.content)
        self.client_ID = jsonBody["id"]
        print(self.client_ID)

    def deletechannel(self, channel_ID):
        payload={'api_key':self.api}
        r = requests.delete("https://api.thingspeak.com/channels/"+channel_ID+".json",json=payload)
        # jsonBody = json.loads(r.content)
        # print(jsonBody)

if __name__ == "__main__":
    conf=json.load(open("settings.json"))
    broker = conf["broker"]
    port = conf["port"]
    apikey=conf["apikey_giulio"]
    ts=TSadaptor(broker,port,apikey)
    ts.run()
    # ts.createnewchannel("prova")
    # ts.deletechannel("1335340")
