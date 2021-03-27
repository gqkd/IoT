import telepot
from telepot.loop import MessageLoop
import json
import requests
import cherrypy
import sys
sys.path.append("C://Users\marco\Dropbox (Politecnico Di Torino Studenti)\POLITO\I Programming for IoT application\Esercitazioni\MQTT")
from MyMQTT import *

class RESTBot:
    exposed = True
    def __init__ (self,token):
        # Local token        
        self.tokenBot=token
        # Catalog token
        #self.tokenBot=requests.get("http://catalogIP/telegram_token").json()["telegramToken"]        
        self.bot=telepot.Bot(self.tokenBot)
        self.chatIDs = []
        self.__messages = {"alert":"","action":""}
        MessageLoop(self.bot,{'chat': self.on_chat_message}).run_as_thread()
        
    def on_chat_message(self,msg):        
        content_type, chat_type ,chat_ID = telepot.glance(msg)        
        # message=msg['text']        
        # self.bot.sendMessage(chat_ID,text="You sent:\n"+message)
        self.chatIDs.append(chat_ID)
    
    def POST(self,*uri):
        tosend = ''
        output ={'status':'not-sent','message':''}
        if len(uri) != 0:
            if uri[0] == 'temp':
                body = cherrypy.request.body.read()
                jsonBody = json.loads(body)
                alert = jsonBody['alert']
                action = jsonBody['action']
                tosend = f"ATTENCTION!!!\n{alert}, you should {action}"
                output = {'status':'sent','message':tosend}
                for user in self.chatIDs:
                    self.bot.sendMessage(user,text=tosend)
        return json.dumps(output)
                
                
   
        
        
        
        
        
        
if __name__ == "__main__":
    conf = json.load(open("settings.json"))
    token = conf['telegramToken']
    topic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]
    rb = RESTBot(token)
    cherryConf = {
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on':True
        }
    }
    cherrypy.config.update({'server.socket_port': 8070})
    cherrypy.tree.mount(rb,'/',cherryConf)
    cherrypy.engine.start()
    cherrypy.engine.block()
    
    