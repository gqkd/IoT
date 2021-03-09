import cherrypy #ho commentato anche io
import json # ho commentato yeee
import datetime 
import time
class ServerHelper():
     def TimeControl(self,Catalog):
        current_time=time.time()
        k=0
        for i in Catalog["devicesList"]:
            if current_time-i["TimeStamp"] > 15:
                Catalog["devicesList"].pop(k)
            k=k+1

class Server():
    exposed=True 
    def __init__(self):
        self.Catalog={
            "projectOwner":"Davide Pedroncelli",
            "projectName":"Lab05",
            "lastUpdate":str(datetime.time()),
            "devicesList":[],
            "servicesList":[]
            #"usersList":[]
            }
        self.help=ServerHelper()

    def GET(self,*uri,**params):
        self.help.TimeControl(self.Catalog)
        if uri[0]=="GetDevices":
            return  json.dumps(self.Catalog)
        elif uri[0]=="GetDevice":
            chiave = [*params]
            valore = params[chiave[0]]
            print(self.Catalog["devicesList"])
            print(valore)
            for i in self.Catalog["devicesList"]:
                if i["deviceID"]==valore:
                    return json.dumps(i)
                    break

    def PUT(self,*uri):
        self.help.TimeControl(self.Catalog)
        body=cherrypy.request.body.read()
        jsonBody=json.loads(body)
        self.Catalog["lastUpdate"]=str(datetime.time())
        if uri[0]=="Device":
            #Controllo che il device ID se esite in devicesList
            k=0
            for j in self.Catalog["devicesList"]:
                if j["deviceID"]==jsonBody["deviceID"]:
                    self.Catalog["devicesList"].pop(k)
                k=k+1
            self.Catalog["devicesList"].append(jsonBody)
            #print(self.Catalog["devicesList"])
            return json.dumps(self.Catalog)
        elif uri[0]=="Service":
             #Controllo che il Service ID se esite in servicesList
            k=0
            for j in self.Catalog["devicesList"]:
                if j["serviceID"]==jsonBody["serviceID"]:
                    self.Catalog["servicesList"].pop(k)
                k=k+1
            self.Catalog["servicesList"].append(jsonBody)

   

        
if __name__=="__main__":
#Standard configuration to serve the url "localhost:8080"
    conf={'/':{'request.dispatch':cherrypy.dispatch.MethodDispatcher(),'tool.session.on':True}}
    cherrypy.quickstart(Server(),'/',conf)




