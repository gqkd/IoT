import cherrypy
import os
import json
import requests
import webbrowser


class Example(object):
    exposed=True
    def __init__(self):
        pass
    
    def GET(self,*uri,**params):
        if uri:
            if uri[0] == "SelectBoxes":
                return f"User name: {self.name}, password: {self.psw}"
        else:
            return open("Login.html")
      
    def POST(self,*uri,**params):
        body = cherrypy.request.body.read()
        # jsonBody = json.loads(body)
        self.name = params.get('uname')
        self.psw = params.get('psw')
        print(f"User name: {self.name}, Password: {self.psw}")
        webbrowser.open('http://127.0.0.1:8093/SelectBoxes')  # Go to example.com
        return print(body)#json.dumps(jsonBody)




if __name__ == '__main__':
    conf={
        '/':{
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on':True
        }
    }
    cherrypy.config.update({'server.socket_port':8093}) #per cambiare la porta se già impiegata per altro
    cherrypy.tree.mount(Example(),'/',conf)
    cherrypy.engine.start()
    cherrypy.engine.block()
