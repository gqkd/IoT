import json
import time

import requests
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup

from MyMQTT import *


class TelegramBot:
    exposed=True
    def __init__(self, token,broker,port,topic):
        # Local token
        self.tokenBot = token
        # Catalog token
        # self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]
        self.bot = telepot.Bot(self.tokenBot)
        self.chatIDs=[]
        self.client = MyMQTT("telegramBotIoT", broker, port, self)
        self.client.start()
        self.topic = topic
        self.client.mySubscribe(topic)
        self.__message={"alert":"","action":""}
        MessageLoop(self.bot, {'chat': self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()
        
    def topicRequest(self):
        # Richiesta GET per topic dei servizi
        r = requests.get(self.url+"/GetTopic")
        jsonBody = json.loads(r.content)
        listatopicService = jsonBody["topics"]
        for topic in listatopicService:
            # self.client.unsubscribe()
            self.client.mySubscribe(topic)  # TOPIC RICHIESTO A CATALOG
            
    # def request(self):
    #     # Sottoscrizione al boxcatalog
    #     self.payload["Timestamp"] = time.time()
    #     requests.put(self.url+"/Service", json=self.payload)  # Sottoscrizione al Catalog


    
    
    
    
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        if message == "/start":            
            buttons = [[InlineKeyboardButton(text=f'Transport team ', callback_data=f'transport'),
                        InlineKeyboardButton(text=f'Surgical team ', callback_data=f'surgical')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Who are you?', reply_markup=keyboard)
        elif message : #TODO filtrare per capire quando inserisco la box ID 
            boxID = message
            cont = -1
            if self.chatIDs != []:
                for id in self.chatIDs:
                    cont += 1
                    if id["chatID"] == chat_ID:
                        self.chatIDs[cont]["boxID"] = boxID
            self.chatIDs.append({"chatID":chat_ID,"boxID":boxID,"team":})
        
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")
        
        

    
            
    def on_callback_query(self,msg):     #Quando premo un bottone    
        #TODO Salvare nel chatIDs se è surgical o transpor
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')        
        payload = self.__message.copy()        
        payload['e'][0]['v'] = query_data        
        payload['e'][0]['t'] = time.time()        
        self.client.myPublish(self.topic, payload)        
        self.bot.sendMessage(chat_ID, text=f"Led switched {query_data}")
        
    def notify(self,topic,msg):
        
        messaggio= json.loads(msg)
        # messaggio {'Acceleration':1, "DeviceID": 001200}
        
        if messaggio.values[0] == 1:
            boxID = messaggio['DeviceID'][:3:]
            for id in self.chatIDs:
                if id["boxID"] == boxID:
                    tosend=f"ATTENTION!!!\n{messaggio.keys[0]} out of range."
                    chat_ID = id["chatID"]
                    self.bot.sendMessage(chat_ID, text=tosend)
        #TODO aggiungere comando per silenziare l'attuatore 

if __name__ == "__main__":
    conf = json.load(open("../settings.json"))
    token = conf["telegramToken"]

    # Echo bot
    # bot=EchoBot(token)

    # SimpleSwitchBot
    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    topic = "orlando/alert/#"
    #ssb = SimpleSwitchBot(token, broker, port, topic)
    sb=TelegramBot(token,broker,port,topic)

    input("press a key to start...")
    test=MyMQTT("testIoTBot",broker,port,None)
    test.start()
    topic = "orlando/alert/temp"
    for i in range(5):
        message={"alert":i,"action":i**2}
        test.myPublish(topic,message)
        time.sleep(3)