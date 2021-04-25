import cherrypy
import os
import numpy as np
import json
import requests
import webbrowser
import urllib.request
from jinja2 import Environment, FileSystemLoader
import threading
import time
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64


# per jinja2
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
env=Environment(loader=FileSystemLoader(CUR_DIR),
trim_blocks=True)

class WebApp(object):
    exposed=True
    def __init__(self):
        time.sleep(12)
        self.usersData = json.load(open("User_data.json"))
        
        try:
            r = requests.get('http://localhost:4040/api/tunnels')
        except:
            print("!!! except -> GET api ngrok !!!")

        jsonBody=json.loads(r.text)
        self.publicURL=jsonBody["tunnels"][0]["public_url"]
        print(self.publicURL)
        

        # richiesta public url catalog 
        conf=json.load(open("settings.json"))
        apikey = conf["publicURL"]["publicURL_read"]
        cid = conf["publicURL"]["publicURL_channelID"]
        try:
            r = requests.get(f"https://api.thingspeak.com/channels/{cid}/fields/1.json?api_key={apikey}&results=1")
        except:
            print("!!! except -> GET publicURL catalog !!!")

        jsonBody=json.loads(r.text)
        self.url_catalog=jsonBody['feeds'][0]['field1']

        requests.put(self.url_catalog+"/UserData", json=self.usersData) # Invio al catalog il dizionario degli utenti
        self.user = {
                "UserName": None,
                "E-mail":None,
                "Psw": None,
                "Level": None,
                "Hospital": None,
                "Boxes": []
            }
        # inizializzazione Lista ospedali 
        self.listHospital = []
        for user in self.usersData['userList']:
            if user["Hospital"] != "NHS":
                self.listHospital.append(user["Hospital"].replace(" ","_"))
        self.listHospital = list(np.unique(self.listHospital))

                
        

    
    def GET(self,*uri,**params):
        if uri:
            if uri[0] == "Desktop":
                indexDesktop2 = env.get_template('indexDesktop2.html')
                return indexDesktop2.render(listHospital=self.listHospital)
            elif uri[0] == "Mobile":
                indexMobile1 = env.get_template('indexMobile1.html')
                return indexMobile1.render(listHospital=self.listHospital)
            elif uri[0] == "NodeRed1":
                self.NodeRed1 = params["link"]+"/ui"
            elif uri[0] == "NodeRed2":
                self.NodeRed2 = params["link"]+"/ui"
            elif uri[0] == "NodeRed3":
                self.NodeRed3[uri[1]] = params["link"]+"/ui"
            elif uri[0] == "UsersData":
                return json.dumps(self.usersData)
            elif uri[0] == "RegistrationComplete":
                if self.user["UserName"] != None:
                    self.usersData["userList"].append(self.user)
                    try:
                        requests.put(self.url_catalog+"/UserData", json=self.usersData) # invio dati Utenti al catalog ogni volta ho un nuovo sign up
                    except:
                        print("!!! except -> PUT invio dati utenti !!!")
                    print(self.usersData)
                    #appendo ospedale nuovo alla lista degli ospedali
                    if self.user["Level"] == "2": 
                        self.listHospital.append(self.user["Hospital"].replace(" ","_"))
                    #salvo dati utenti nel json
                    with open("User_data.json","w") as f:
                        json.dump(self.usersData , f ,indent=4)
                    
                    self.user = {
                    "UserName": None,
                    "E-mail":None,
                    "Psw": None,
                    "Level": None,
                    "Hospital": None,
                    "Boxes": []
                    }
                    
                    indexDesktop2 = env.get_template('indexDesktop2.html')
                    return indexDesktop2.render(listHospital=self.listHospital)
            
            
            elif uri[0] == "NHSinfo":
                
                
                
                allDataInfo = {}
                BoxDataInfo = {}
                BOXL = []
                for hospital in self.listHospital:
                    DoctorList = []
                    BoxesList = []
                    AssociationDict = []
                    for user in self.usersData['userList']:
                        if user["Hospital"] == hospital.replace("_"," ") and user["Level"] =="3":
                            DoctorList.append(user["UserName"])
                            diz = {user["UserName"]:user["Boxes"]}
                            AssociationDict.append(diz)
                    for user in self.usersData['userList']:
                        if user["Hospital"] == hospital.replace("_"," ") and user["Level"] =="2":
                            BoxesList = user["Boxes"]
                            BOXL.extend(BoxesList)
                    
                    description = f"<p>Available Boxes:</p> {BoxesList}<br><p>Doctors of the Hospital:</p> {DoctorList}<br><p>Associations:</p> {AssociationDict}"
                    description = description.replace("{","")
                    description = description.replace("}","")
                    description = description.replace("[]","None")
                    description = description.replace("[","")
                    description = description.replace("]","")
                    description =description.replace("'","")
                    allDataInfo[hospital.replace("_"," ")] = description
               
                BOXL  = list(np.unique(BOXL))
                for box in BOXL:
                    L =[]
                    D = ["None"]
                    for user in self.usersData['userList']:
                        print(user["Boxes"])
                        if user["Boxes"]!=[]:
                            if user["Boxes"][0]== box and user["Level"]=="3":
                                L.append(user["UserName"])
                            if box in user["Boxes"] and user["Level"]=="2":
                                D[0]=user["Hospital"]
                    if L!=[]:
                        d = f"<p>Hospital:</p> {D}<br><p>Association:</p> {L}"
                        d = d.replace("[","")
                        d = d.replace("]","")
                        d = d.replace("'","")
                        BoxDataInfo[box] = d
                    else: 
                        d = f"<p>Hospital:</p> {D}<br><p>Association:</p> The box has not been associated with any user."  
                        d = d.replace("[","")
                        d = d.replace("]","")
                        d =d.replace("'","")
                        BoxDataInfo[box] =  d  
                indexDesktop5 = env.get_template('indexDesktop5.html')
                return indexDesktop5.render(listHospital=self.listHospital, allDataInfo = allDataInfo,BoxDataInfo = BoxDataInfo)

        else:
            indexDesktop2 = env.get_template('indexDesktop2.html')
            return indexDesktop2.render(listHospital=self.listHospital)
      
    def POST(self,*uri,**params):
        body = cherrypy.request.body.read()
        if uri[0] == "Registration" or uri[0] == "RegistrationMobile":
            self.user["UserName"] = params.get('uname')
            self.user["Psw"] = params.get('psw')
            self.user["E-mail"] = params.get('mail')
            if params.get('type') == "NHS":
                self.user["Hospital"] = "NHS"
                self.user["Level"] = "1"
            elif params.get('type') == "Hospital":
                self.user["Hospital"] = params.get('hospital').replace("_" ," ")
                self.user["Level"] = "2"
            elif params.get('type') == "Doctor":
                self.user["Hospital"] = params.get('hospital').replace("_" ," ")
                self.user["Level"] = "3"
            print(self.user)
            self.SendEmail(self.user["E-mail"],self.user["UserName"],self.user["Psw"])
            if uri[0] == "Registration":
                indexDesktop2 = env.get_template('indexDesktop2.html')
                return indexDesktop2.render(listHospital=self.listHospital)
            else:
                indexMobile1 = env.get_template('indexMobile1.html')
                return indexMobile1.render(listHospital=self.listHospital)
        

        elif uri[0] == "Desktop" or uri[0] == "Mobile":
           
            name = params.get('uname')
            psw = params.get('psw')
            print(self.usersData['userList'])
            for user in self.usersData['userList']:
                if user["UserName"] == name:
                    if user["Psw"] == psw:
                        if user["Level"] == "1":
                            return urllib.request.urlopen(self.publicURL+'/NHSinfo')
                        
                        elif user["Level"] == "2":
                            L_user = []
                            L_box = user["Boxes"]
                            for c,i in enumerate(self.usersData['userList']):
                                if i["Hospital"] == user["Hospital"] and i["Level"] == "3":
                                    L_user.append(self.usersData['userList'][c]["UserName"])
                            indexDesktop3 = env.get_template('indexDesktop3.html')
                            UHospital = user['Hospital'].replace(" " ,"_")
                            return  indexDesktop3.render(listUsers=L_user, listBoxes = L_box, UserHospital = UHospital,urlNodered2 = self.NodeRed2),     

                        elif user["Level"] == "3":
                            indexMobile3 = env.get_template('indexMobile3.html')
                            return indexMobile3.render(urlNodered3 = self.NodeRed3[user["Boxes"]])
                    else:
                        if uri[0] == "Desktop":
                            indexDesktop4 = env.get_template('indexDesktop4.html')
                            return indexDesktop4.render(listHospital=self.listHospital) #TODO dovremmo dirgli che la psw è cannata return urllib.request.urlopen(self.URL)
                        else:
                            indexMobile2 = env.get_template('indexMobile2.html')
                            return indexMobile2.render(listHospital=self.listHospital) #TODO dovremmo dirgli che la psw è cannata return urllib.request.urlopen(self.URL)



            #print(f"User name: {name}, Password: {psw}")
        elif uri[0] == "AssociateBox":
            if params.get('user1') != "None" and params.get('box1') != "None":
                for c,user in enumerate(self.usersData['userList']):
                    if user["UserName"] == params.get('user1'):
                        if self.usersData['userList'][c]["Boxes"] != []:
                            self.usersData['userList'][c]["Boxes"][0] = params.get('box1')
                        else:
                            self.usersData['userList'][c]["Boxes"].append(params.get('box1'))
                        
            if params.get('user2') != "None" and params.get('box2') != "None":
                for c,user in enumerate(self.usersData['userList']):
                    if user["UserName"] == params.get('user2'):
                        if self.usersData['userList'][c]["Boxes"] != []:
                            self.usersData['userList'][c]["Boxes"][0] = params.get('box2')
                        else:
                            self.usersData['userList'][c]["Boxes"].append(params.get('box2'))
                        
            if params.get('user3') != "None" and params.get('box3') != "None":
                for c,user in enumerate(self.usersData['userList']):
                    if user["UserName"] == params.get('user3'):
                        if self.usersData['userList'][c]["Boxes"] != []:
                            self.usersData['userList'][c]["Boxes"][0] = params.get('box3')
                        else:
                            self.usersData['userList'][c]["Boxes"].append(params.get('box3'))
                        
            with open("User_data.json","w") as f:
                json.dump(self.usersData , f ,indent=4)                
            L_user = []
            
            Hospital = params.get('UHospital').replace("_" ," ")
            for c,user in enumerate(self.usersData['userList']):
                if user["Hospital"] == Hospital and user["Level"] == "2":
                    L_box = user["Boxes"]
            
            for c,i in enumerate(self.usersData['userList']):
                if i["Hospital"] == user["Hospital"] and i["Level"] == "3":
                    L_user.append(self.usersData['userList'][c]["UserName"])
            indexDesktop3 = env.get_template('indexDesktop3.html')
            UHospital = user['Hospital'].replace(" " ,"_")
            
            try:
                requests.put(self.url_catalog+"/UserData", json=self.usersData) # invio dati Utenti al catalog ogni volta ho un nuovo sign up
            except:
                print("!!! except -> PUT invio dati utenti !!!")
                        
            return indexDesktop3.render(listUsers=L_user, listBoxes = L_box, UserHospital = UHospital)

        elif uri[0] == "AddBox":
            boxID = params.get('boxID')
            Hospital = params.get('UHospital')
            Hospital = Hospital.replace("_" ," ")
            for c,user in enumerate(self.usersData['userList']):
                if user["Hospital"] == Hospital and user["Level"] == "2":
                    self.usersData['userList'][c]["Boxes"].append(boxID)
                    with open("User_data.json","w") as f:
                        json.dump(self.usersData , f ,indent=4)
                    L_box = user["Boxes"]
            L_user = []   
            for c,i in enumerate(self.usersData['userList']):
                if i["Hospital"] == user["Hospital"] and i["Level"] == "3":
                    L_user.append(self.usersData['userList'][c]["UserName"])
            indexDesktop3 = env.get_template('indexDesktop3.html')
            UHospital = user['Hospital'].replace(" " ,"_")
            try:
                requests.put(self.url_catalog+"/UserData", json=self.usersData) # invio dati Utenti al catalog ogni volta ho un nuovo sign up
            except:
                print("!!! except -> PUT invio dati utenti !!!")
            
            return indexDesktop3.render(listUsers=L_user, listBoxes = L_box, UserHospital = UHospital)
        
        elif uri[0] == "RemoveBox":
            boxID = params.get('boxID')
            Hospital = params.get('UHospital')
            Hospital = Hospital.replace("_" ," ")
            for c1,user in enumerate(self.usersData['userList']):
                if user["Hospital"] == Hospital and user["Level"] == "2":
                    for c2,box in enumerate(user["Boxes"]):
                        if box == boxID:
                           self.usersData['userList'][c1]["Boxes"].pop(c2) 
                    with open("User_data.json","w") as f:
                        json.dump(self.usersData , f ,indent=4)
                    L_box = user["Boxes"]
            L_user = []   
            for c,i in enumerate(self.usersData['userList']):
                if i["Hospital"] == user["Hospital"] and i["Level"] == "3":
                    L_user.append(self.usersData['userList'][c]["UserName"])
            indexDesktop3 = env.get_template('indexDesktop3.html')
            UHospital = user['Hospital'].replace(" " ,"_")
            
            try:
                requests.put(self.url_catalog+"/UserData", json=self.usersData) # invio dati Utenti al catalog ogni volta ho un nuovo sign up
            except:
                print("!!! except -> PUT invio dati utenti !!!")
                        
            return indexDesktop3.render(listUsers=L_user, listBoxes = L_box, UserHospital = UHospital)
        
        # elif uri[0] == "NodeRed2":
        #     return json.dumps(self.NodeRed2+'/ui/#!/0')
 

    def SendEmail(self, email, user, psw):
        
        sender_email = "IoTorgandelivery@gmail.com"
        receiver_email = email
        port = 465  # For SSL
        password = "Organ1111"
        message = MIMEMultipart("alternative")
        message["Subject"] = "Confirmation of Registration"
        message["From"] = sender_email
        message["To"] = receiver_email
        # Create the plain-text and HTML version of your message
        text = f"""\
        Hi,
        Thank you for subscribing to IoT Platform for smart organ delivery.
        username: {user}
        password: {psw}
        Click the following link to complete your registration:
        {self.publicURL}/RegistrationComplete
        """
        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login("IoTorgandelivery@gmail.com", password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("email inviata!")

class cherry:
    def __init__(self):
        conf={
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tool.session.on':True
        },
		 '/css':{
		 'tools.staticdir.on': True,
		 'tools.staticdir.dir':'./css'
		 },
		#  '/js':{
		#  'tools.staticdir.on': True,
		#  'tools.staticdir.dir':'./js'
		#  },
	}
        cherrypy.config.update({'server.socket_port':8095}) 
        cherrypy.tree.mount(WebApp(),'/',conf)
        cherrypy.engine.start()
        cherrypy.engine.block()

class ngrok:
    def __init__(self):
        time.sleep(5)
        # os.system('ngrok authtoken 1jrtviNE8MpMMqrakaml6JI68HK_2t6ahDqgiKPxPdQiqXK5k')
        os.system('ngrok http -subdomain=SmartOrganDelivery 8095')


if __name__ == '__main__':
    # è necessario startare 3 thread per il tunnelling
    t1 = threading.Thread(target=cherry)
    t2 = threading.Thread(target=ngrok)

    t1.start()
    t2.start()
