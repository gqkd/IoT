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
        r= requests.get('http://localhost:4040/api/tunnels/<WebApp>')
        self.URL=r.json()["public_url"]

    
    def GET(self,*uri,**params):
        if uri:
            if uri[0] == "SelectBoxes":
                return f"User name: {self.name}, password: {self.psw}"
        else:
            return open("index1.html")
      
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
                        return urllib.request.urlopen('http://4b77ad6cf4c3.ngrok.io/ui/#!/0')
                    elif user["Level"] == "2":
                        return urllib.request.urlopen('http://c17e5be40643.ngrok.io/ui')
                    elif user["Level"] == "3":
                        return urllib.request.urlopen('http://c17e5be40643.ngrok.io/ui')
                else:
                    return urllib.request.urlopen(self.URL)

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
    cherrypy.config.update({'server.socket_port':8094}) #per cambiare la porta se già impiegata per altro
    cherrypy.tree.mount(Example(),'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()