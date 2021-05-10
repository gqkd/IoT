import paho.mqtt.client as mqtt
import json
import time

class MyMQTT:
    def __init__(self, clientID, broker, port, notifier):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.client_id = clientID
        self._topic = ""
        self._isSubscriber = False
        self._client = mqtt.Client(clientID, True) #creo istanza client
        self._client.on_connect = self.myon_connect #registro callback on_connect
        self._client.on_message = self.myon_message  #registro callback on_message
        # self._client.on_subscribe = self.myon_subscribe
        self.start() #richiamo lo start del thread

    def myon_connect(self, _client, userdata, flags, rc):
        print ("\n%s Connected to %s with result code: %d\n" % (self.client_id, self.broker, rc))
    
    # def myon_subscribe(self,client, userdata, mid, granted_qos):
    #     self._client.loop_stop()
    
    def start(self):
        try:
            self._client.connect(self.broker, self.port) #connetto al broker
        except: #se non si connette al broker esce dall'esecuzione del programma
            print("\nNot connected to the broker %s", self.broker)
            # quit()
        self._client.loop_start() #starta il thread per il loop
        
    def myPublish(self, topic, msg):
        # self._client.loop_start()
        pubs=self._client.publish(topic, json.dumps(msg), 2)
        if pubs[0]==0:
            pass
            # print("%s published:\n %s\n to topic: %s\n" % (self.client_id,json.dumps(msg), topic))
        else:
            print("\nMessage NOT published to topic %s" % (topic))

    def myon_message(self, _client, userdata, msg):
        self.notifier.notify (msg.topic, msg.payload)
        # print (f"\nmessage: {msg.payload} \n")
        # self._client.loop_stop()

    def mySubscribe(self, topic): #non sono riuscito a fare una prova con un errore di iscrizione al topic
        # self._client.loop_start()
        subs=self._client.subscribe(topic, 2)
        self._isSubscriber = True
        self._topic = topic
        if subs[0]==0:
            pass
            # print("%s subscibed to topic: %s\n" % (self.client_id, topic))
        else:
            print("\n %s NOT subscibed to topic %s\n" % (self.client_id,topic))

    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._client.unsubscribe(self._topic)
            
    def stop (self):
        if (self._isSubscriber):
            self._client.unsubscribe(self._topic)
        self._client.loop_stop()
        self._client.disconnect()