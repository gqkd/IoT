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
    def __init__(self,broker,port,apikey,write_api,read_api,channel_ID): 
        conf=json.load(open("settings.json"))
        apikey2 = conf['apikey_read_bea']
        cid = conf['channel_ID_publicURL']
        r = requests.get(f"https://api.thingspeak.com/channels/{cid}/fields/1.json?api_key={apikey2}&results=1")

        jsonBody=json.loads(r.text)
        # print(r.text, r, r.content)
        self.url=jsonBody['feeds'][0]['field1']
        self.serviceID = "TSadaptor"
        self.broker = broker
        self.port = port
        self.api = apikey
        self.diz_write_api = write_api
        self.diz_channel_ID = channel_ID
        self.diz_read_api = read_api
        self.client = MyMQTT(self.serviceID, self.broker, self.port, self)
        self.client.start()
        # self.t = threading.Thread(target=self.notify)


    def topicsearch(self):
        r=requests.get(self.url+"/Dumpitallmodafaccar")
        # print(r.text,r.status_code)
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
        id_num = payload['bn']
        #richiesta per avere la lista dei canali presenti
        r = requests.get("https://api.thingspeak.com/channels.json?api_key="+self.api)
        jsonBody = json.loads(r.content)
        # print(json.dumps(jsonBody, indent=2))
        # print(jsonBody[0]['name'])
        canalebox=0
        for channel in range(len(jsonBody)):
            nomecanale = jsonBody[channel]['name']
            if nomecanale == str(id_num): #il canale c'è
                canalebox=1
        # if not canalebox:
        #     if num_sensore == '100':
        #         self.createnewchannel2(str(id_num),)

        if num_sensore == '100': #temp
            if not canalebox:
                self.createnewchannel2(str(id_num),'temperatura')
            val = payload['e'][0]['v']
            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api['100']}&field1={str(val)}")
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
        elif num_sensore == '200': #acc
            if not canalebox:
                self.createnewchannel2(str(id_num),'accelerazione')
            x = payload['e'][0]["v_xaxis"]
            y = payload['e'][0]["v_yaxis"]
            z = payload['e'][0]["v_zaxis"]
            val = sqrt(x**2+y**2+z**2)
            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api['200']}&field1={str(val)}")
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
        elif num_sensore == '300': #mass
            pass
        elif num_sensore == '400': #oxy
            if not canalebox:
                self.createnewchannel2(str(id_num),'ossigenazione')
            val = payload['e'][0]['v']
            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api['400']}&field1={str(val)}")
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
        elif num_sensore == '500': #speaker
            pass
        elif num_sensore == '600': #GPS
            if not canalebox:
                self.createnewchannel2(str(id_num),'coordinate')
            val={'v_lat':payload['e'][0]['v_lat'],'v_lon':payload['e'][0]['v_lon']}
            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api['600']}&field1={str(val)}")
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
        else:
            print("!!!!!!!!!!!!!!!!!!!!!! sensore non riconosciuto !!!!!!!!!!!!!!!!!!")


    def run(self):
        while True:
            self.topicsearch()
            time.sleep(30)
    
    def createnewchannel2(self, nome_canale, nome_field):
        payload={
            'api_key':self.api,
            'field1':nome_field,
            'name':nome_canale, 
            'public_flag':True,
        }
        r = requests.post("https://api.thingspeak.com/channels.json",json=payload)
        # print(r.text)
        jsonBody = json.loads(r.content)
        channel_ID = jsonBody["id"]
        write_api = jsonBody['api_keys'][0]['api_key']
        read_api = jsonBody['api_keys'][1]['api_key']
        self.diz_write_api[f'{nome_canale[3::]}']=write_api
        self.diz_channel_ID[f'{nome_canale[3::]}']=channel_ID
        self.diz_read_api[f'{nome_canale[3::]}']=read_api
        # print(json.dumps(jsonBody,indent=2))
        # print(self.write_api)
        with open('settings.json') as fp:
            actual=json.load(fp)
            actual['write_api']=self.diz_write_api
            actual['channel_ID']=self.diz_channel_ID
            actual['read_api']= self.diz_read_api
        with open('settings.json','w') as pd:
            json.dump(actual, pd,indent=2)
        print(f"nuovo canale creato id:{self.diz_channel_ID}")

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
    read_api=conf['read_api']
    channel_ID=conf['channel_ID']
    ts=TSadaptor(broker,port,apikey,write_api,read_api,channel_ID)
    ts.run()

