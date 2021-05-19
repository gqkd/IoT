from MyMQTT import *
import time
import requests
import json
from math import sqrt


class TSadaptor:
    def __init__(self,conf,numerobox):
        apikey_publicURL= conf["publicURL"]["publicURL_read"]
        cid = conf["publicURL"]["publicURL_channelID"]
        try:
            r = requests.get(f"https://api.thingspeak.com/channels/{cid}/fields/1.json?api_key={apikey_publicURL}&results=1")
        except:
            print("!!! except -> richiesta publicURL !!!")
        jsonBody=json.loads(r.text)
        self.numerobox = numerobox
        self.url=jsonBody['feeds'][0]['field1']
        self.serviceID = "TSadaptor"+self.numerobox+"kdjghsldigu"
        self.broker = conf["broker"]
        self.port = conf["port"]
        self.api_service = conf["canaleServizio"]["canaleServizio_general"]
        self.diz_write_api_service = conf["canaleServizio"]["canaleServizio_write"]
        self.diz_channel_ID_service = conf["canaleServizio"]["canaleServizio_channel"]
        self.diz_read_api_service = conf["canaleServizio"]["canaleServizio_read"]
        self.diz_write_api = conf["canaliSensori"]["canaliSensori_write"]
        self.diz_channel_ID = conf["canaliSensori"]["canaliSensori_channel"]
        self.diz_read_api = conf["canaliSensori"]["canaliSensori_read"]
        self.client = MyMQTT(self.serviceID, self.broker, self.port, self)
        self.client.start()
        self.config = conf

    def topicsearch(self):
        try:
            r = requests.get(self.url+"/Get_TSadaptor")
        except:
            print("!!!except -> GET boxcatalog!!!")
        jsonBody = json.loads(r.content)
        listatopicServices = jsonBody["services"]
        listatopicDevices = jsonBody["devices"]
        for t2 in range(len(listatopicDevices)):
            if listatopicDevices[t2]['Resource']!='Speaker':
                self.client.mySubscribe(listatopicDevices[t2]['Topic'])
        for element in listatopicServices:
            if "healthControl" in element["Topic"]:
                self.client.mySubscribe(element["Topic"])

    def notify(self, topic, msg):
        payload = json.loads(msg)
        print(f"\nInoltro a TS Messaggio: {payload}")
        if 'bn' in list(payload.keys()):
            num_sensore = payload['bn'][3::]
            id_num = payload['bn']
            if self.numerobox == payload['bn'][:3:]:
                self.api_device = conf["canaliSensori"]["canaliSensori_general"][0]
            else:
                self.api_device = conf["canaliSensori"]["canaliSensori_general"][1]
            #richiesta per avere la lista dei canali presenti
            try:
                r = requests.get("https://api.thingspeak.com/channels.json?api_key="+self.api_device)
            except:
                print("!!! except -> GET lista canali presenti !!!")
            jsonBody = json.loads(r.content)


            canalebox=0
            for channel in range(len(jsonBody)):
                nomecanale = jsonBody[channel]['name']
                if nomecanale == str(id_num):
                    canalebox=1

            if num_sensore == '100': #temp
                if not canalebox:
                    self.createnewchannel2(str(id_num),'temperatura',self.api_device)
                val = payload['e'][0]['v']
                r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api[id_num]}&field1={str(val)}")
                print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
            elif num_sensore == '200': #acc
                if not canalebox:
                    self.createnewchannel2(str(id_num),'accelerazione',self.api_device)
                x = payload['e'][0]["v_xaxis"]
                y = payload['e'][0]["v_yaxis"]
                z = payload['e'][0]["v_zaxis"]
                val = sqrt(x**2+y**2+z**2)
                r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api[id_num]}&field1={str(val)}")
                print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
            elif num_sensore == '300': #mass
                pass
            elif num_sensore == '400': #oxy
                if not canalebox:
                    self.createnewchannel2(str(id_num),'ossigenazione',self.api_device)
                val = payload['e'][0]['v']
                r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api[id_num]}&field1={str(val)}")
                print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
            elif num_sensore == '500': #speaker
                pass
            elif num_sensore == '600': #GPS
                if not canalebox:
                    self.createnewchannel2(str(id_num),'coordinate',self.api_device)
                val={'v_lat':payload['e'][0]['v_lat'],'v_lon':payload['e'][0]['v_lon'],'v_time':payload['e'][0]['v_time']}
                r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api[id_num]}&field1={str(val)}")
                print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
            else:
                print("!!! sensore non riconosciuto !!!")
        else:
            try:
                r = requests.get("https://api.thingspeak.com/channels.json?api_key=" + self.api_service)
            except:
                print("!!! except -> GET lista canali presenti !!!")
            jsonBody = json.loads(r.content)

            flag = 0
            listanomicanali=[]
            for element in jsonBody:
                listanomicanali.append(element['name'])
            nomecanale = list(payload.keys())[0] + 'Health_Status'
            
            if nomecanale in listanomicanali:
                flag = 1
                print("il canale c'è")
            if flag==0:
                print("il canale non c'è")
                self.createnewchannel(nomecanale,'Health Control', self.api_service)
            try:
                val = payload[self.numerobox]['Health Status']
                r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api_service[nomecanale]}&field1={str(val)}")
                print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")
            except:
                pass

    def run(self):
        while True:
            self.topicsearch()
            r = requests.put(self.url + "/Info", json=self.config)
            time.sleep(30)

    # PER SENSORI
    def createnewchannel2(self, nome_canale, nome_field, api):
        payload={
            'api_key':api,
            'field1':nome_field,
            'name':nome_canale, 
            'public_flag':True,
        }
        try:
            r = requests.post("https://api.thingspeak.com/channels.json",json=payload)
        except:
            print("!!! except -> POST creazione canale !!!")
        jsonBody = json.loads(r.content)
        channel_ID = jsonBody["id"]
        write_api = jsonBody['api_keys'][0]['api_key']
        read_api = jsonBody['api_keys'][1]['api_key']
        self.diz_write_api[f'{nome_canale}']=write_api
        self.diz_channel_ID[f'{nome_canale}']=channel_ID
        self.diz_read_api[f'{nome_canale}']=read_api
        with open('settings.json') as fp:
            actual=json.load(fp)
            actual["canaliSensori"]["canaliSensori_write"]=self.diz_write_api
            actual["canaliSensori"]["canaliSensori_channel"]=self.diz_channel_ID
            actual["canaliSensori"]["canaliSensori_read"]= self.diz_read_api
        with open('settings.json','w') as pd:
            json.dump(actual, pd,indent=2)
        print(f"nuovo canale creato id:{self.diz_channel_ID}")

    # PER SERVIZIO HEALTH CONTROL STATUS
    def createnewchannel(self, nome_canale, nome_field, api):
        payload={
            'api_key':api,
            'field1':nome_field,
            'name':nome_canale,
            'public_flag':True,
        }
        try:
            r = requests.post("https://api.thingspeak.com/channels.json",json=payload)
        except:
            print("!!! except -> POST creazione canale !!!")
        jsonBody = json.loads(r.content)
        channel_ID = jsonBody["id"]
        write_api = jsonBody['api_keys'][0]['api_key']
        read_api = jsonBody['api_keys'][1]['api_key']
        self.diz_write_api_service[f'{nome_canale}']=write_api
        self.diz_channel_ID_service[f'{nome_canale}']=channel_ID
        self.diz_read_api_service[f'{nome_canale}']=read_api

        with open('settings.json') as fp:
            actual=json.load(fp)
            actual["canaleServizio"]["canaleServizio_write"]=self.diz_write_api_service
            actual["canaleServizio"]["canaleServizio_channel"]=self.diz_channel_ID_service
            actual["canaleServizio"]["canaleServizio_read"]= self.diz_read_api_service
        with open('settings.json','w') as pd:
            json.dump(actual, pd,indent=2)
        print(f"nuovo canale creato id:{self.diz_channel_ID_service}")

    def deletechannel(self, channel_ID):
        payload={'api_key':self.api}
        r = requests.delete("https://api.thingspeak.com/channels/"+channel_ID+".json",json=payload)


if __name__ == "__main__":
    conf=json.load(open("settings.json"))

    ts=TSadaptor(conf,'001')
    ts2 = TSadaptor(conf,'002')
    ts.run()
    ts2.run()
