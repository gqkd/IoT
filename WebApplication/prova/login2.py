import cherrypy
import os
import json
import requests
import webbrowser


class Example(object):
    exposed=True
    def __init__(self):
        self.usersData = json.load(open("User_data.json"))
        self.userList = self.usersData['userList']
    
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
                        webbrowser.open('http://127.0.0.1:1880/ui/#!/1?socketid=UEeRYcvctN0-raE8AAAA')
                    elif user["Level"] == "2":
                        pass
                    elif user["Level"] == "3":
                        pass
                else:
                    return "User name or password uncorrect"

        
        
        print(f"User name: {self.name}, Password: {self.psw}")
        webbrowser.open('http://127.0.0.1:8094/SelectBoxes')  # Go to example.com
        return print(body)#json.dumps(jsonBody)



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