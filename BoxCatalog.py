import cherrypy
import json
import datetime
import time

class Catalog():
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
        
    def PUT(self,*uri): # Registrare Sensori o Service nel catalog
        body=cherrypy.request.body.read()
        jsonBody=json.loads(body)
        if uri[0] == "Device":
            cont = -1
            for box in self.deviceList:
                cont += 1
                if str(box["deviceID"]) == str(jsonBody["deviceID"]): # Controllo se esiste gia il sensore e nel caso la elimino
                    #
                    self.deviceList.pop(cont)
            self.deviceList.append(jsonBody)
            print(self.deviceList)
            return json.dumps(self.deviceList)

            
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
        if len(uri)!=0:
            if uri[0] == "GetTemperature":
                return json.dumps({"topics" : "Ipfsod/+/+/temperature"})
            elif uri[0] == "GetAcceleration":
                return json.dumps({"topics" : "Ipfsod/+/+/acceleration"})
            elif uri[0] == "GetMass":
                return json.dumps({"topics" : "Ipfsod/+/+/mass"})
            elif uri[0] == "GetOxygenLevel":
                return json.dumps({"topics" : "Ipfsod/+/+/oxygen"})
          
            #----------------
            
            # elif uri[0]=="GetDevice":
            #     chiave = list(params.keys())
            #     chiave = chiave[0]
            #     id=params[chiave]
            #     for diz in self.catalog["devicesList"]:
            #         if diz["DeviceID"]==id:
            #             return json.dumps(diz)
                        
            # elif uri[0] == "GetService":
            #     id = params["DeviceID"]
                
            #     for diz in self.catalog["servicesList"]:
            #         if diz["DeviceID"] == id:
            #             print(diz)
            #             return json.dumps(diz)
            # elif uri[0] == "GetTSadaptor": # serve tutto
            #     return "sa,sa,sa prova 1,2,3, sa, sa"     
        
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
    
    #tunneling il nostro url è https://boxcatalog.loca.lt
    # la prima volta, prima di lanciare lo script digitare da terminale "npm install -g localtunnel"
    # per l'installazione dei moduli
    # nota se usate delle VPN disattivatele perchè non gli piacciono
    # resp=os.system('lt --port 8070 --subdomain boxcatalog') #killare la connessione precedente
    #inserire controllo per url giusto
    # print(resp)
    # while True:
    #     # Catalog().TimeControl()
    #     time.sleep(10)
    # cherrypy.engine.block()
    
    
