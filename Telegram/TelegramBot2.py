import json
import time
import threading
import requests
import telepot
import os
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

import sys
sys.path.append("C://Users\marco\Dropbox (Politecnico Di Torino Studenti)\POLITO\I Programming for IoT application\Esercitazioni\MQTT")
from MyMQTT import *


class TelegramBot(threading.Thread):
    exposed=True
    def __init__(self, token,broker,port):
        threading.Thread.__init__(self)
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        self.chatIDs=[]
        self.client = MyMQTT("telegramBotIoT", broker, port, self)
        self.client.start()
        # self.canSendBoxID = 0 #per leggere box id solo quando viene chiesto
        MessageLoop(self.bot, {'chat': self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()
        # Dati utili per il timing
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timerequestTopic = conf2["timerequestTopic"]
        self.timerequest = conf2["timerequest"]
        # richiesta public url catalog 
        conf=json.load(open("settings.json"))
        apikey = conf["publicURL"]["publicURL_read"]
        cid = conf["publicURL"]["publicURL_channelID"]
        r = requests.get(f"https://api.thingspeak.com/channels/{cid}/fields/1.json?api_key={apikey}&results=1")
        jsonBody=json.loads(r.text)
        self.url_catalog=jsonBody['feeds'][0]['field1']
        # # richiesta public url Web Application 
        # conf=json.load(open("settings.json"))
        # apikey = conf["publicURL"]["publicURL_read"]
        # cid = conf["publicURL"]["publicURL_channelID"]
        # r = requests.get(f"https://api.thingspeak.com/channels/{cid}/fields/1.json?api_key={apikey}&results=1")
        # jsonBody=json.loads(r.text)
        # self.url_webApp=jsonBody['feeds'][0]['field1']
        # messaggio inviato all'attuatore
        self.topic = conf["baseTopic"]
        self.payload = {
            "serviceID": "06_TelegramBot",
            "Topic": f"{self.topic}/06_TelegramBot/telegramBot",
            "Resource": "TelegramBot",
            "Timestamp": None
        }
        r = requests.get(self.url_catalog+"/GetUserData") #richiesta elenco utenti WebApp
        self.usersData = json.loads(r.content)
        
    def topicRequest(self):
        # Richiesta GET per topic dei servizi
        r = requests.get(self.url_catalog+"/GetServiceTopic") 
        jsonBody = json.loads(r.content)
        listatopicService = jsonBody["topics"]
        for topic in listatopicService:
            self.client.mySubscribe(topic)
        r = requests.get(self.url_catalog+"/GetGPS")
        jsonBody = json.loads(r.content)
        self.client.mySubscribe(jsonBody["topics"][0])    # TOPIC gps RICHIESTO A CATALOG

            
    def request(self):
        # Sottoscrizione al boxcatalog
        self.payload["Timestamp"] = time.time()
        requests.put(self.url_catalog+"/Service", json=self.payload)  # Sottoscrizione al Catalog

    def run(self):
        count = 6
        while True:
            self.topicRequest()
            if count % (self.timerequest/self.timerequestTopic) == 0:
                self.request()
                count=0
            count += 1
            time.sleep(self.timerequestTopic)
    
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        flag = 0
        if self.chatIDs != []:
            for c,id in enumerate(self.chatIDs):
                if id["chatID"] == chat_ID:
                    cont = c
                    flag = 1 # per sapere se l'id della chat non è presente
        
                  
        
        message = msg['text']
        if message == "/start":            
            self.bot.sendMessage(chat_ID, text=f"Insert insert your user ID e pasword: \nE.g. 'user01-psw01'" )
            if flag == 1:
                self.chatIDs[cont]["Notification"][4] = 1
            else:
                self.chatIDs.append({"chatID":chat_ID,"boxID":None,"team":None,"Notification":[1,1,1,"ON",1]}) # Notification ha tre flag per disattivare le tre notifiche: partenza, 20min left, arrivato,notifiche telegram, controllo che inserisco userID-psw solo quando chiesto
                
        # elif message == "/changeboxid":
        #     self.bot.sendMessage(chat_ID, text=f"Insert Box ID: ")
        #     self.chatIDs[cont]["Notification"][4] = 1
        #     # self.canSendBoxID = 1
        elif self.chatIDs[cont]["Notification"][4] == 1:
            r = requests.get(self.url_catalog+"/GetUserData") #richiesta elenco utenti WebApp al catalog
            self.usersData = json.loads(r.content)
            user = message.split("-")
            userID = user[0]
            psw = user[1]
            
            for user in self.usersData['userList']:
                if user["UserName"] == userID:
                    if user["Psw"] == psw:
                        boxID = user["Boxes"]
                        self.chatIDs[cont]["boxID"] = boxID
                        self.chatIDs[cont]["Notification"] = [1,1,1,"ON",0]
                        
                        buttons = [[InlineKeyboardButton(text=f'Transport team ', callback_data=f'transport'),
                        InlineKeyboardButton(text=f'Surgical team ', callback_data=f'surgical')]]
                        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
                        self.bot.sendMessage(chat_ID, text='Who are you?', reply_markup=keyboard)
                        
                    else:
                        self.bot.sendMessage(chat_ID, text=f"Invalid user ID or password. \nTry again: ")

                
        elif message == "/allarmoff":
            buttons = [[InlineKeyboardButton(text=f'Temperature', callback_data=f'TemperatureOFF'),
                        InlineKeyboardButton(text=f'Acceleration', callback_data=f'AccelerationOFF'),
                        InlineKeyboardButton(text=f'Oxygen', callback_data=f'OxygenOFF')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Which alarm do you want to silence?', reply_markup=keyboard)
        elif message == "/allarmon":
            buttons = [[InlineKeyboardButton(text=f'Temperature', callback_data=f'TemperatureON'),
                        InlineKeyboardButton(text=f'Acceleration', callback_data=f'AccelerationON'),
                        InlineKeyboardButton(text=f'Oxygen', callback_data=f'OxygenON')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Which alarm do you want to activate?', reply_markup=keyboard)
        elif message == "/finish":
            self.chatIDs.pop(cont)
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")
        print(self.chatIDs)
        

    
            
    def on_callback_query(self,msg):     #Quando premo un bottone    
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        if self.chatIDs != []:
            for c,id in enumerate(self.chatIDs):
                if id["chatID"] == chat_ID:
                    cont = c
        
        if query_data[-2:] == "ON":
            boxID = self.chatIDs[cont]["boxID"]
            self.chatIDs[cont]["Notification"][3] = query_data[-2:]
            
            messaggio = {query_data[:-2]: "ON", "DeviceID": boxID}
            self.client.myPublish(self.payload["Topic"], messaggio)
            self.bot.sendMessage(chat_ID, text=f"{query_data}")
            
        elif query_data[-3:] == "OFF":
            boxID = self.chatIDs[cont]["boxID"]
            self.chatIDs[cont]["Notification"][3] = query_data[-3:]
            
            messaggio = {query_data[:-3]: "OFF", "DeviceID": boxID}
            self.client.myPublish(self.payload["Topic"], messaggio)
            self.bot.sendMessage(chat_ID, text=f"{query_data}")

        else:
            self.chatIDs[cont]["team"] = query_data
            self.bot.sendMessage(chat_ID, text=f"Registered as {query_data} team. You will receive notifications from Box {self.chatIDs[cont]['boxID']}.")
            
        
    def notify(self,topic,msg):

        messaggio= json.loads(msg)
        print(messaggio)
        print(topic)
        # messaggio {
            # 'bn': self.deviceID,
            # 'e': [
            #         {
            #             'n': 'GPS',
            #             'u': 'DD',
            #             't': None,
            #             'v_lat': None,
            #             'v_lon': None,
            #             'v_time': None
            #         }
            #     ]
            # }
        # messaggio {'Acceleration':1, "DeviceID": 001200}
        
        if topic[-3:] == "GPS":           
            boxID = messaggio["bn"][:3:]           
            for cont,id in enumerate(self.chatIDs):
                if id["boxID"] == boxID:
                    chat_ID = id["chatID"]
                    if id["Notification"][0] == 1 and id["team"] == "surgical":
                        self.bot.sendMessage(chat_ID, text=f"Your Box {boxID} is on its way.")
                        self.chatIDs[cont]["Notification"][0] = 0
                        
            if messaggio["e"][0]["v_time"] < 20:  # Parte da 120
                for cont,id in enumerate(self.chatIDs):
                    if id["boxID"] == boxID:
                        chat_ID = id["chatID"]
                        if id["Notification"][1] ==1 and id["team"] == "surgical":
                            self.bot.sendMessage(chat_ID, text=f"Your Box {boxID} will arrive in 20 min.")
                            self.chatIDs[cont]["Notification"][1] = 0    
                                                
            if messaggio["e"][0]["v_time"] < 1:
                for cont,id in enumerate(self.chatIDs):
                    if id["boxID"] == boxID:
                        chat_ID = id["chatID"]
                        if id["Notification"][2] == 1 and id["team"] == "surgical":
                            self.bot.sendMessage(chat_ID, text=f"Your Box ({boxID}) is arrived!")
                            self.chatIDs[cont]["Notification"][2] = 0
  
        
        else:
            valori = list(messaggio.values())
            chiavi = list(messaggio.keys())
            if valori[0] == 1 and chiavi[0] != "Mass":
                boxID = messaggio['DeviceID'][:3:]
                for id in self.chatIDs:
                    if id["boxID"] == boxID:
                        if id["team"] == "transport" and id["Notification"][3] == "ON":
                            chiavi = list(messaggio.keys())
                            tosend=f"ATTENTION!!!\n{chiavi[0]} out of range."
                            chat_ID = id["chatID"]
                            self.bot.sendMessage(chat_ID, text=tosend)
        
    def stop_MyMQTT(self):
        self.client.stop()

if __name__ == "__main__":
    conf = json.load(open("settings_bot.json"))
    token = conf["telegramToken"]

    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    
    tb=TelegramBot(token,broker,port)
    tb.start()
    while True:
        time.sleep(100)
    

