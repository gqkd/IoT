import cherrypy
import os
import json
import requests
import webbrowser
import urllib.request
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
class Example(object):
    exposed=True
    def __init__(self):
        self.usersData = json.load(open("User_data.json"))
        self.user = {
                "UserName": None,
                "E-mail":None,
                "Psw": None,
                "Level": None,
                "Hospital": None,
                "Boxes": []
            }
        #r = requests.get('http://localhost:4040/api/tunnels/WebApp')
        
        #self.public_ur = r.json()["public_url"] #"http://localhost:8094" #r.json()["public_url"]
        #print(self.public_ur)
        

    
    def GET(self,*uri,**params):
        if uri:
            if uri[0] == "Desktop":
                return open("indexDesktop.html")
            elif uri[0] == "Mobile":
                return open("indexMobile.html")
            elif uri[0] == "NodeRed1":
                self.NodeRed1 = params["link"]
            elif uri[0] == "NodeRed2":
                self.NodeRed2 = params["link"]
            elif uri[0] == "NodeRed3":
                self.NodeRed3 = params["link"]
            elif uri[0] == "UsersData":
                return json.dumps(self.usersData)
            elif uri[0] == "RegistrationComplete":
                self.usersData["userList"].append(self.user)
                print(self.usersData)
                with open("User_data.json","w") as f:
                   json.dump(self.usersData, f)
                return open("indexDesktop.html")

        else:
            return open("indexDesktop.html")
      
    def POST(self,*uri,**params):
        body = cherrypy.request.body.read()
        print(f"&>&&&&&&&&&{params}")
        if uri[0] == "Registration":
            self.user["UserName"] = params.get('uname')
            self.user["Psw"] = params.get('psw')
            self.user["E-mail"] = params.get('mail')
            print(self.user)
            self.SendEmail(self.user["E-mail"])
            return open("indexDesktop.html")
        elif uri[0] == "Desktop" or uri[0] == "Mobile":
            name = params.get('uname')
            psw = params.get('psw')
            for user in self.usersData['userList']:
                if user["UserName"] == name:
                    if user["Psw"] == psw:
                        if user["Level"] == "1":
                            print("ok!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                            return urllib.request.urlopen(self.NodeRed1+'/ui/#!/0')
                        elif user["Level"] == "2":
                            return urllib.request.urlopen(self.NodeRed2+'/ui/#!/0')
                        elif user["Level"] == "3":
                            return urllib.request.urlopen(self.NodeRed3+'/ui/#!/0')
                    else:
                        pass #return urllib.request.urlopen(self.URL)

            print(f"User name: {self.name}, Password: {self.psw}")

    def SendEmail(self, email):
        
        sender_email = "IoTorgandelivery@gmail.com"
        receiver_email = email
        port = 465  # For SSL
        password = "Organ1111"
        message = MIMEMultipart("alternative")
        message["Subject"] = "Confirmation of Registration"
        message["From"] = sender_email
        message["To"] = receiver_email
        # Create the plain-text and HTML version of your message
        text = """\
        Hi,
        Thank you for subscribing to IoT Platform for smart organ delivery.

        Click the following link to complete your registration:
        http://127.0.0.1:8095/RegistrationComplete
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


if __name__ == '__main__':
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
    cherrypy.tree.mount(Example(),'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()