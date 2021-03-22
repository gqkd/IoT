import cherrypy
import json
import datetime
import time
import os
import requests
import threading

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
                    self.deviceList.pop(cont)
            self.deviceList.append(jsonBody)
            print(f"""Lista device attivi: \n {self.deviceList}""")
            return json.dumps(self.deviceList)

        elif uri[0] == "Service":
            cont = -1
            for service in self.servicesList:
                cont += 1
                if str(service["serviceID"]) == str(jsonBody["serviceID"]):
                    self.servicesList.pop(cont)
            self.servicesList.append(jsonBody)
            print(f"""Lista servizi attivi: \n {self.servicesList}""")
            return json.dumps(self.servicesList)

        self.catalog["lastUpdate"] = str(datetime.time())
        
    def GET(self,*uri):
        if len(uri)!=0:
            # Posso farmi tornare anche topic a cui si sottoscrive speaker?
            if uri[0] == "GetTemperature":
                return json.dumps({"topics" : "Ipfsod/+/+/temperature"})
            elif uri[0] == "GetAcceleration":
                return json.dumps({"topics" : "Ipfsod/+/+/acceleration"})
            elif uri[0] == "GetMass":
                return json.dumps({"topics" : "Ipfsod/+/+/mass"})
            elif uri[0] == "GetOxygenLevel":
                return json.dumps({"topics" : "Ipfsod/+/+/oxygen"})
            elif uri[0] == "GetTopic":
                return json.dumps(({'topics':["Ipfsod/+/temperatureControl","Ipfsod/+/accelerationControl","Ipfsod/+/oxygenControl","Ipfsod/+/weightControl" ]}))
            elif uri[0] == "Dumpitallmodafaccar":
                return json.dumps({'services':self.servicesList,'devices':self.deviceList})
            #----------------

    # CHI LA RICHIAMA STA FUNZIONE? UN CAZZO DI NESSUNO, QUINDI NON CREDO VADA EHEH
    def TimeControl(self):
        cont_device = 0
        cont_service = 0
        for device in self.deviceList:
            if time.time()-device["Timestamp"] > 120:
                self.deviceList.pop(cont_device)
                return print(f"Device deleted: {device}")
            cont_device += 1
        for service in self.servicesList:
            if time.time()-service["Timestamp"] > 120:
                self.servicesList.pop(cont_service)
                return print(f"Service deleted: {service}")
            cont_service += 1

class cherry:
    def __init__(self):
        
        conf={
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on':True
        }
        }
        cherrypy.config.update({'server.socket_port': 8070})
        cherrypy.tree.mount(Catalog(),'/',conf)
        cherrypy.engine.start()
        

class ngrok:
    def __init__(self):
        time.sleep(5)
        os.system('ngrok http 8070')

class tunneling:
    def __init__(self):
        time.sleep(10)
        #leggo il publicURL dall'api di ngrok
        r = requests.get('http://localhost:4040/api/tunnels')
        jsonBody=json.loads(r.text)
        publicURL=jsonBody["tunnels"][0]["public_url"]
        print(publicURL)
        #invio il publicURL sul canale Thingspeak creato apposta
        r1 = requests.get("https://api.thingspeak.com/update?api_key=KKQGIYEG410H7T0L&field1="+publicURL)
        print(r1.text)

if __name__=="__main__":
    # è necessario startare 3 thread per il tunnelling
    t1 = threading.Thread(target=cherry)
    t2 = threading.Thread(target=ngrok)
    t3 = threading.Thread(target=tunneling)

    t1.start()
    t2.start()
    t3.start()

    #se si vuole usare il tunneling commentare queste funzione e decommentare sopra
    # cherry()

    


    
    
