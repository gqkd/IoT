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

    def topicsearch(self):
        r=requests.get(self.url+"/Dumpitallmodafaccar")
        jsonBody = json.loads(r.content)
        listatopicServices = jsonBody["services"]
        listatopicDevices = jsonBody["devices"]
        # print(listatopicServices)

        for t1 in range(len(listatopicServices)):
            self.client.mySubscribe(listatopicServices[t1]['Topic']) 
        for t2 in range(len(listatopicDevices)):
            if listatopicDevices[t2]['Resource']!='Speaker':
                self.client.mySubscribe(listatopicDevices[t2]['Topic'])
        

    def notify(self, topic, msg):
        msg_sensore=0
        msg_servizio=0
        payload = json.loads(msg)
        payloadkeys = list(payload.keys())
        print(f"Messagggggggio: {payload}")
        if payloadkeys[0] == 'bn': #messaggio dal sensore
            id_box = payload["bn"][:3:]
            num_sensore = payload['bn'][3::]
            val = payload['e'][0]['v']
            print(val,type(val)) #arrivato qui, bisogna aggiustare per l'accelerazione che è un casino, tmp la prende bene...unica
            msg_sensore=1
        else: #messaggio dal servizio
            id_box = payload["DeviceID"][:3:]
            msg_servizio=1
        #richiesta per avere la lista dei canali presenti
        r = requests.get("https://api.thingspeak.com/channels.json?api_key="+self.api)
        jsonBody = json.loads(r.content)
        # print(json.dumps(jsonBody, indent=2))
        # print(jsonBody[0]['name'])
        canalepresente=0
        for channel in range(len(jsonBody)):
            nomecanale = jsonBody[channel]['name']
            if nomecanale == str(id_box):
                canalepresente=1
                break
            else:
                canalepresente=0
        if not canalepresente:
            self.createnewchannel(str(id_box))
        #buttare i dati nel posto giusto
        # if msg_sensore:
        #     if num_sensore == '100': #temp
        #         r = requests.get("https://api.thingspeak.com/update?api_key="+write_api+"&field6="+str(val))
        #     elif num_sensore == '200': #acc
        #         r = requests.get("https://api.thingspeak.com/update?api_key="+write_api+"&field2="+str(val))
        #     elif num_sensore == '400': #oxy
        #         r = requests.get("https://api.thingspeak.com/update?api_key="+write_api+"&field4="+str(val))

        

    def run(self):
        while True:
            self.topicsearch()
            time.sleep(10)

    def createnewchannel(self, nome_canale):
        payload={
            'api_key':self.api,
            'field1':"OrganHealth",
            'field2':"Acceleration",
            'field3':"Acc_control",
            'field4':"OxygenLevel",
            'field5':"Oxy_control",
            'field6':"Temperature",
            'field7':"Temp_control",
            #posizione da aggiungere
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

