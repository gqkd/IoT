import cherrypy
import json
import requests
import datetime
import time
import threading

class Catalog(threading.Thread):
    exposed=True
    def __init__(self):
        self.catalog = {
            "projectOwner": "Marco Bonfanti", 
            "projectName": "Laboratorio 5", 
            "lastUpdate": str(datetime.time()), 
            "devicesList": [],
            "servicesList": []
        }
        self.devicesList = self.catalog['devicesList']
        
    def PUT(self,*uri):
        body=cherrypy.request.body.read()
        jsonBody=json.loads(body)
        if uri[0] == "Device":
            
            cont = -1
            for diz in self.catalog["devicesList"]:
                cont += 1
                if diz["DeviceID"] == jsonBody["DeviceID"]:
                    self.catalog["devicesList"].pop(cont)
            self.catalog["devicesList"].append(jsonBody)
            print(self.catalog["devicesList"])
            
        elif uri[0] == "Service":
            cont = -1
            for diz in self.catalog["servicesList"]:
                cont += 1
                if diz["DeviceID"] == jsonBody["DeviceID"]:
                    self.catalog["servicesList"].pop(cont)
                self.catalog["servicesList"].append(jsonBody)
            self.catalog["servicesList"].append(jsonBody)
            print(self.catalog["devicesList"])
        self.catalog["lastUpdate"] = str(datetime.time())
        
    def GET(self,*uri,**params):
        if uri[0] == "GetDevices":
            print(self.catalog["devicesList"])
            return json.dumps(self.catalog["devicesList"])
        elif uri[0]=="GetDevice":
            chiave = list(params.keys())
            chiave = chiave[0]
            id=params[chiave]
            for diz in self.catalog["devicesList"]:
                if diz["DeviceID"]==id:
                    return json.dumps(diz)
                    
        elif uri[0] == "GetService":
            id = params["DeviceID"]
            
            for diz in self.catalog["servicesList"]:
                if diz["DeviceID"] == id:
                    print(diz)
                    return json.dumps(diz)
                
    def TimeControl(self):
        cont = -1
        for diz in self.catalog['devicesList']:
            cont += 1
            if time.time()-float(diz["Timestamp"]) > 2:
                self.catalog['devicesList'].pop(cont)

        
        
        
        
        
        
if __name__=="__main__":
    #Standard configuration to serve the url "localhost:8080"
    conf={
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on':True
        }
    }
    cherrypy.config.update({'server.socket_port': 8070})
    cherrypy.tree.mount(Catalog(),'/',conf)
    cherrypy.engine.start()
    while True:
        Catalog().TimeControl()
        time.sleep(10)
    cherrypy.engine.block()
    
    
