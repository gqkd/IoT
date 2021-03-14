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
            "projectOwner": "Bonfanti_Pedroncelli_Quaglia_Zanchi", 
            "projectName": "IoT platform for smart organs delivery", 
            "lastUpdate": str(datetime.time()), 
            "deviceList": [],
            "servicesList": []
        }
        self.deviceList = self.catalog['deviceList']
        self.servicesList = self.catalog['servicesList']
        
    def PUT(self,*uri): # Registrare Box o Service nel catalog
        body=cherrypy.request.body.read()
        jsonBody=json.loads(body)
        if uri[0] == "Device":
            
            cont = -1
            for box in self.boxList:
                cont += 1
                if box["deviceID"] == jsonBody["deviceID"]: # Controllo se esiste gia la Box e nel caso la elimino
                    self.deviceList.pop(cont)
            self.deviceList.append(jsonBody)
            print(self.deviceList)
            
        elif uri[0] == "Service":
            cont = -1
            for service in self.servicesList:
                cont += 1
                if service["serviceID"] == jsonBody["serviceID"]:
                    self.servicesList.pop(cont)
            self.servicesList.append(jsonBody)
            print(self.servicesList)
            
        self.catalog["lastUpdate"] = str(datetime.time())
        
    def GET(self,*uri):
        if uri[0] == "GetTemperature":
            # topic = {"topics" : []}
            # for sensor in self.boxList["sensors"]:
            #     if sensor["Resource"] == "Temperature":
            #         topic["topics"].append(sensor["Topic"])
            # return json.dumps(topic)
            return json.dumps({"topics" : "Ipfsod/+/+/Temperature"})
        
        
        #----------------
        
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
    
    
