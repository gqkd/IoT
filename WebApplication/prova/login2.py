import cherrypy
import os
import json
import requests
import webbrowser
import urllib.request


class Example(object):
    exposed=True
    def __init__(self):
        self.usersData = json.load(open("User_data.json"))
        self.userList = self.usersData['userList']
        r = requests.get('http://localhost:4040/api/tunnels/WebApp')
        
        self.public_ur = r.json()["public_url"] #"http://localhost:8094" #r.json()["public_url"]
        print(self.public_ur)
        

    
    def GET(self,*uri,**params):
        if uri:
            if uri[0] == "SelectBoxes":
                return f"User name: {self.name}, password: {self.psw}"
            elif uri[0] == "Desktop":
                return open("indexDesktop.html")
            elif uri[0] == "Mobile":
                return open("indexMobile.html")
            elif uri[0] == "NodeRed1":
                self.NodeRed1 = params["link"]
            elif uri[0] == "NodeRed2":
                self.NodeRed2 = params["link"]
            elif uri[0] == "NodeRed3":
                self.NodeRed3 = params["link"]
                
        else:
            return open("indexDesktop.html")
      
    def POST(self,*uri,**params):
        body = cherrypy.request.body.read()
        # jsonBody = json.loads(body)
        self.name = params.get('uname')
        self.psw = params.get('psw')
        
        for user in self.userList:
            if user["UserName"] == self.name:
                if user["Psw"] == self.psw:
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
    cherrypy.config.update({'server.socket_port':8094}) 
    cherrypy.tree.mount(Example(),'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()