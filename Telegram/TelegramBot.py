import json
import time
import threading
import requests
import telepot
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
        self.canSendBoxID = 0 #per leggere box id solo quando viene chiesto
        MessageLoop(self.bot, {'chat': self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()
        # Dati utili per il timing
        conf2 = json.load(open("settingsboxcatalog.json"))
        self.timerequestTopic = conf2["timerequestTopic"]
        self.timerequest = conf2["timerequest"]
        self.count = 6
        
    def topicRequest(self):
        # Richiesta GET per topic dei servizi
        r = requests.get(self.url+"/GetTopic") 
        jsonBody = json.loads(r.content)
        listatopicService = jsonBody["topics"]
        self.client.mySubscribe(listatopicService[0])  # TOPIC temp RICHIESTO A CATALOG
        self.client.mySubscribe(listatopicService[1])  # TOPIC acc RICHIESTO A CATALOG
        self.client.mySubscribe(listatopicService[2])  # TOPIC oxyg RICHIESTO A CATALOG
        r = requests.get(self.url+"/GetGPS") #TODO 
        jsonBody = json.loads(r.content)
        self.client.mySubscribe(jsonBody["topics"])    # TOPIC gps RICHIESTO A CATALOG
            
    # def request(self):
    #     # Sottoscrizione al boxcatalog
    #     self.payload["Timestamp"] = time.time()
    #     requests.put(self.url+"/Service", json=self.payload)  # Sottoscrizione al Catalog



    def run(self):
        while True:
            self.topicRequest()
            # if self.count % (self.timerequest/self.timerequestTopic) == 0:
            #     # self.request()
            #     if self.dizionario_misure != {}:
            #         print('CIAONEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
            #         self.calcolo_healthstatus()
            #         self.client.myPublish(f"{self.topic}/{self.serviceID}/healthControl", self.dizionario_misure)
            #     self.count=0
            # self.count += 1
            time.sleep(self.timerequestTopic)
    
    
    
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']
        if message == "/start":            
            buttons = [[InlineKeyboardButton(text=f'Transport team ', callback_data=f'transport'),
                        InlineKeyboardButton(text=f'Surgical team ', callback_data=f'surgical')]]
            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            self.bot.sendMessage(chat_ID, text='Who are you?', reply_markup=keyboard)
        elif message == "/changeboxid":
            self.bot.sendMessage(chat_ID, text=f"Insert Box ID: ")
            self.canSendBoxID = 1
        elif self.canSendBoxID == 1:
            #TODO valutare una richiesta al catalog per avere una lista di tutti i sensori sottoscritti e quindi le box per verificare che l'boxID inserito sia presente nel catalog
            boxID = message
            if len(boxID) == 3:
                cont = -1
                flag = 0 #per sapere se l'id della chat non è presente
                if self.chatIDs != []:
                    for id in self.chatIDs:
                        cont += 1
                        if id["chatID"] == chat_ID:
                            self.chatIDs[cont]["boxID"] = boxID
                            flag = 1
                if flag == 0 or self.chatIDs == []:
                    self.chatIDs.append({"chatID":chat_ID,"boxID":boxID,"team":None,"Notification":[1,1,1]}) # Notification ha tre flag per disattivare le tre notifiche: partenza, 20min left, arrivato
                self.bot.sendMessage(chat_ID, text=f"Registered to Box {boxID}.")
                self.canSendBoxID = 0
            else: 
                self.bot.sendMessage(chat_ID, text=f"Invalid Box ID. Try again.")
        else:
            self.bot.sendMessage(chat_ID, text="Command not supported")
        print(self.chatIDs)
        

    
            
    def on_callback_query(self,msg):     #Quando premo un bottone    
        query_ID , chat_ID , query_data = telepot.glance(msg,flavor='callback_query')
        
        cont = -1
        flag = 0
        if self.chatIDs != []:
            for id in self.chatIDs:
                cont += 1
                if id["chatID"] == chat_ID:
                    self.chatIDs[cont]["team"] = query_data
                    flag = 1
        if flag == 0 or self.chatIDs == []:
                self.chatIDs.append({"chatID":chat_ID,"boxID":None,"team":query_data,"Notification":[1,1,1]})

        self.bot.sendMessage(chat_ID, text=f"Registered as {query_data} team.")
        self.bot.sendMessage(chat_ID, text=f"Insert Box ID: ")
        self.canSendBoxID = 1
        print(self.chatIDs)
        
    def notify(self,topic,msg):

        messaggio= json.loads(msg)
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
        if topic[3:] == "GPS":
            boxID = messaggio["bn"][:3:]
            
            cont = -1
            for id in self.chatIDs:
                cont += 1
                if id["boxID"] == boxID:
                    chat_ID = id["chatID"]
                    if id["Notification"][0] == 1:
                        self.bot.sendMessage(chat_ID, text=f"Your Box ({boxID}) is on its way.")
                        self.chatIDs[cont]["Notification"][0] = 0
                            
            if messaggio["e"]["v_time"] < 20:
                cont = -1
                for id in self.chatIDs:
                    cont += 1
                    if id["boxID"] == boxID:
                        chat_ID = id["chatID"]
                        if id["Notification"][1] == 1:
                            self.bot.sendMessage(chat_ID, text=f"Your Box ({boxID}) will arrive in 20 min.")
                            self.chatIDs[cont]["Notification"][1] = 0
                            
            if messaggio["e"]["v_time"] < 1:
                cont = -1
                for id in self.chatIDs:
                    cont += 1
                    if id["boxID"] == boxID:
                        chat_ID = id["chatID"]
                        if id["Notification"][2] == 1:
                            self.bot.sendMessage(chat_ID, text=f"Your Box ({boxID}) is arrived!")
                            self.chatIDs[cont]["Notification"][2] = 0

  
        
        else:
            if messaggio.values[0] == 1:
                boxID = messaggio['DeviceID'][:3:]
                for id in self.chatIDs:
                    if id["boxID"] == boxID:
                        tosend=f"ATTENTION!!!\n{messaggio.keys[0]} out of range."
                        chat_ID = id["chatID"]
                        self.bot.sendMessage(chat_ID, text=tosend)
            #TODO aggiungere comando per silenziare l'attuatore 
        
    def stop_MyMQTT(self):
        self.client.stop()

if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    token = conf["telegramToken"]

    broker = conf["brokerIP"]
    port = conf["brokerPort"]
    
    tb=TelegramBot(token,broker,port)
    tb.start()
    for i in range(100):
        time.sleep(100)
    

    # input("press a key to start...")
    # test=MyMQTT("testIoTBot",broker,port,None)
    # test.start()
    # topic = "orlando/alert/temp"
    # for i in range(5):
    #     message={"alert":i,"action":i**2}
    #     test.myPublish(topic,message)
    #     time.sleep(3)