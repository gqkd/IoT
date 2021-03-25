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
from math import sqrt
import threading

class TSadaptor:
    def __init__(self,broker,port,apikey,write_api,channel_ID): 
        #unica cosa che serve per certo è l'indirizzo del box catalog
        #TODO qua la richiesta va rifatta bene per prendere l'url così non va bene
        r = requests.get("https://api.thingspeak.com/channels/1333953/fields/1.json?api_key=12YLI1DSAWUJS27X&results=1")
        jsonBody=json.loads(r.text)
        self.url=jsonBody['feeds'][0]['field1']
        self.serviceID = "TSadaptor"
        self.broker = broker
        self.port = port
        self.api = apikey
        self.write_api = write_api
        self.channel_ID = channel_ID
        self.client = MyMQTT(self.serviceID, self.broker, self.port, self)
        self.client.start()
        # self.t = threading.Thread(target=self.notify)
        self.cont=0

    def topicsearch(self):
        r=requests.get(self.url+"/Dumpitallmodafaccar")
        jsonBody = json.loads(r.content)
        # listatopicServices = jsonBody["services"]
        listatopicDevices = jsonBody["devices"]
        # print(listatopicServices)

        # for t1 in range(len(listatopicServices)):
        #     self.client.mySubscribe(listatopicServices[t1]['Topic']) 
        for t2 in range(len(listatopicDevices)):
            if listatopicDevices[t2]['Resource']!='Speaker':
                self.client.mySubscribe(listatopicDevices[t2]['Topic'])
        

    def notify(self, topic, msg):
        payload = json.loads(msg)
        print(f"Messagggggggggggio: {payload}")
        id_box = payload["bn"][:3:]
        num_sensore = payload['bn'][3::]

        #richiesta per avere la lista dei canali presenti
        r = requests.get("https://api.thingspeak.com/channels.json?api_key="+self.api)
        jsonBody = json.loads(r.content)
        # print(json.dumps(jsonBody, indent=2))
        # print(jsonBody[0]['name'])
        canalebox=0
        for channel in range(len(jsonBody)):
            nomecanale = jsonBody[channel]['name']
            if nomecanale == str(id_box): #il canale c'è
                canalebox=1
        if not canalebox:
            self.createnewchannel(str(id_box))

        if num_sensore == '100': #temp
            val = payload['e'][0]['v']
          
            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.write_api}&field1={str(val)}")

            
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
        elif num_sensore == '200': #acc
            x = payload['e'][0]["v_xaxis"]
            y = payload['e'][0]["v_yaxis"]
            z = payload['e'][0]["v_zaxis"]
            val = sqrt(x**2+y**2+z**2)

            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.write_api}&field2={str(val)}")

            
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
        elif num_sensore == '300': #mass
            pass
        elif num_sensore == '400': #oxy
            val = payload['e'][0]['v']

            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.write_api}&field3={str(val)}")

            
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
        elif num_sensore == '500': #speaker
            pass
        elif num_sensore == '600': #GPS
            val={'v_lat':payload['e'][0]['v_lat'],'v_lon':payload['e'][0]['v_lon']}
            
            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.write_api}&field4={str(val)}")
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
        else:
            print("!!!!!!!!!!!!!!!!!!!!!! sensore non riconosciuto !!!!!!!!!!!!!!!!!!")
        self.cont += 1
        print(f"-------------------------------{self.cont}--------------------------")
        #buttare i dati nel posto giusto
        # if msg_sensore:
        # if num_sensore == '100': #temp
        #     r = requests.get("https://api.thingspeak.com/update?api_key="+write_api+"&field2="+str(val))
        # elif num_sensore == '200': #acc
        #     r = requests.get("https://api.thingspeak.com/update?api_key="+write_api+"&field1="+str(val))
        # elif num_sensore == '400': #oxy
        #     r = requests.get("https://api.thingspeak.com/update?api_key="+write_api+"&field3="+str(val))

        

    def run(self):
        
        while True:
            self.topicsearch()
            time.sleep(30)
            

    def createnewchannel(self, nome_canale):
        payload={
            'api_key':self.api,
            'field1':"Temperature",
            'field2':"Acceleration",
            'field3':"Oxygenation",
            'field4':"Lat & Long",
            'name':nome_canale,
            'public_flag':True,
        }
        r = requests.post("https://api.thingspeak.com/channels.json",json=payload)
        jsonBody = json.loads(r.content)
        self.channel_ID = jsonBody["id"]
        self.write_api = jsonBody['api_keys'][0]['api_key']
        # print(json.dumps(jsonBody,indent=2))
        # print(self.write_api)
        with open('settings.json') as fp:
            actual=json.load(fp)
            actual['write_api']=self.write_api
            actual['channel_ID']=self.channel_ID
        with open('settings.json','w') as pd:
            json.dump(actual, pd,indent=2)
        print(f"nuovo canale creato id:{self.channel_ID}")
        


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
    write_api=conf['write_api']
    channel_ID=conf['channel_ID']
    ts=TSadaptor(broker,port,apikey,write_api,channel_ID)
    ts.run()

