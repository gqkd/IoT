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


class TSadaptor:
    def __init__(self,conf):
        broker = conf["broker"]
        port = conf["port"]
        apikey_device=conf["canaliSensori"]["canaliSensori_general"]
        apikey_service = conf["canaleServizio"]["canaleServizio_general"]
        write_api=conf["canaliSensori"]["canaliSensori_write"]
        write_api_service = conf["canaleServizio"]["canaleServizio_write"]
        read_api=conf["canaliSensori"]["canaliSensori_read"]
        read_api_service = conf["canaleServizio"]["canaleServizio_read"]
        channel_ID=conf["canaliSensori"]["canaliSensori_channel"]
        channel_ID_service = conf["canaleServizio"]["canaleServizio_channel"]
        apikey_publicURL= conf["publicURL"]["publicURL_read"]
        cid = conf["publicURL"]["publicURL_channelID"]
        r = requests.get(f"https://api.thingspeak.com/channels/{cid}/fields/1.json?api_key={apikey_publicURL}&results=1")
        jsonBody=json.loads(r.text)
        # print(r.text, r, r.content)
        self.url=jsonBody['feeds'][0]['field1']
        self.serviceID = "TSadaptor"
        self.broker = broker
        self.port = port
        self.api_service = apikey_service
        self.api_device = apikey_device
        self.diz_write_api = write_api
        self.diz_write_api_service = write_api_service
        self.diz_channel_ID = channel_ID
        self.diz_channel_ID_service = channel_ID_service
        self.diz_read_api = read_api
        self.diz_read_api_service = read_api_service
        self.client = MyMQTT(self.serviceID, self.broker, self.port, self)
        self.client.start()
        # self.t = threading.Thread(target=self.notify)
        self.config = conf

    def topicsearch(self):
        r = requests.get(self.url+"/Get_TSadaptor")
        # print(r.text,r.status_code)
        jsonBody = json.loads(r.content)
        listatopicServices = jsonBody["services"]
        listatopicDevices = jsonBody["devices"]
        # print(listatopicServices)

        # for t1 in range(len(listatopicServices)):
        #     self.client.mySubscribe(listatopicServices[t1]['Topic']) 
        for t2 in range(len(listatopicDevices)):
            if listatopicDevices[t2]['Resource']!='Speaker':
                self.client.mySubscribe(listatopicDevices[t2]['Topic'])
        for element in listatopicServices:
            if "healthControl" in element["Topic"]:
                self.client.mySubscribe(element["Topic"])

    def notify(self, topic, msg):
        payload = json.loads(msg)
        print(f"Messagggggggggggio: {payload}")
        if 'bn' in list(payload.keys()):
            num_sensore = payload['bn'][3::]
            id_num = payload['bn']
            #richiesta per avere la lista dei canali presenti
            r = requests.get("https://api.thingspeak.com/channels.json?api_key="+self.api_device)
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
                print("!!!!!!!!!!!!!!!!!!!!!! sensore non riconosciuto !!!!!!!!!!!!!!!!!!")
        else:
            r = requests.get("https://api.thingspeak.com/channels.json?api_key=" + self.api_service)
            jsonBody = json.loads(r.content)
            print(json.dumps(jsonBody,indent=2))
            flag = 0
            listanomicanali=[]
            for element in jsonBody:
                listanomicanali.append(element['name'])
            nomecanale = list(payload.keys())[0] + 'Health_Status'
            # print(type(list(payload.keys())[0]), list(payload.keys())[0], type(nomecanale), nomecanale)
            if nomecanale in listanomicanali:
                flag = 1
                print("il canale c'è")
            if flag==0:
                print("il canale non c'è")
                self.createnewchannel(nomecanale,'Health Control', self.api_service)
            val = payload[str(list(payload.keys())[0])]['Health Status']
            # print(type(val), val)
            r = requests.get(f"https://api.thingspeak.com/update?api_key={self.diz_write_api_service[nomecanale]}&field1={str(val)}")
            print(f"mandato a TS con risultato: {r.status_code} e messaggio {r.text}")

    def run(self):
        while True:
            self.topicsearch()
            r = requests.put(self.url + "/Info", json=self.config)
            # r = requests.put(self.url+"/UpdateConfig", json=self.config)
            # print("config uppato con risultato", r.status_code)
            time.sleep(30)

    # PER SENSORI
    def createnewchannel2(self, nome_canale, nome_field, api):
        payload={
            'api_key':api,
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
        self.diz_write_api[f'{nome_canale}']=write_api
        self.diz_channel_ID[f'{nome_canale}']=channel_ID
        self.diz_read_api[f'{nome_canale}']=read_api
        # print(json.dumps(jsonBody,indent=2))
        # print(self.write_api)
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
        r = requests.post("https://api.thingspeak.com/channels.json",json=payload)
        # print(r.text)
        jsonBody = json.loads(r.content)
        channel_ID = jsonBody["id"]
        write_api = jsonBody['api_keys'][0]['api_key']
        read_api = jsonBody['api_keys'][1]['api_key']
        self.diz_write_api_service[f'{nome_canale}']=write_api
        self.diz_channel_ID_service[f'{nome_canale}']=channel_ID
        self.diz_read_api_service[f'{nome_canale}']=read_api
        # print(json.dumps(jsonBody,indent=2))
        # print(self.write_api)
        with open('settings.json') as fp:
            actual=json.load(fp)
            actual["canaleServizio"]["canaleServizio_write"]=self.diz_write_api_service
            actual["canaleServizio"]["canaleServizio_channel"]=self.diz_channel_ID_service
            actual["canaleServizio"]["canaleServizio_read"]= self.diz_read_api_service
        with open('settings.json','w') as pd:
            json.dump(actual, pd,indent=2)
        print(f"nuovo canale creato id:{self.diz_channel_ID_service}")

    # def deletechannel(self, channel_ID):
    #     payload={'api_key':self.api}
    #     r = requests.delete("https://api.thingspeak.com/channels/"+channel_ID+".json",json=payload)
    #     # jsonBody = json.loads(r.content)
    #     # print(jsonBody)

if __name__ == "__main__":
    conf=json.load(open("settings.json"))
    
    ts=TSadaptor(conf)
    ts.run()

