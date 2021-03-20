import paho.mqtt.client as mqtt
import json
import time

class MyMQTT2:
    def __init__(self, clientID, broker, port, notifier):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.client_id = clientID
        self._isSubscriber = False
        self._client = mqtt.Client(clientID, True) #creo istanza client
        self._client.on_connect = self.myon_connect #registro callback on_connect
        self._client.on_message = self.myon_message  #registro callback on_message
        self.start() #richiamo lo start del thread

    def myon_connect(self, _client, userdata, flags, rc):
        print ("\n%s connected to %s with result code: %d\n" % (self.client_id, self.broker, rc))

    def start(self):
        try:
            self._client.connect(self.broker, self.port) #connetto al broker
        except: #se non si connette al broker esce dall'esecuzione del programma
            print("\nNot connected to the broker %s\n", self.broker)
            quit()
        self._client.loop_start() #starta il thread per il loop
        
    def myPublish(self, topic, msg):
        pubs=self._client.publish(topic, json.dumps(msg), 2)
        if pubs[0]==0:
            print("%s published:\n %s\n to topic: %s" % (self.client_id,json.dumps(msg), topic))
        else:
            print("message NOT published to topic %s" % (topic))

    def myon_message(self, _client, userdata, msg):
        self.notifier.notify (msg.topic, msg.payload)
        print ("\nmessage: %s \n" % (str(msg.payload))) #c'è una cazzo di b' davanti che non capisco come cazzo si toglie porco dio

    def mySubscribe(self, topic): #non sono riuscito a fare una prova con un errore di iscrizione al topic
        subs=self._client.subscribe(topic, 2)
        if subs[0]==0:
            print("\n%s subscibed to topic: %s\n" % (self.client_id, topic))
        else:
            print("\n%s NOT subscibed to topic %s\n" % (self.client_id,topic))

    def unsubscribe(self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._client.unsubscribe(self._topic)
            
    def stop (self):
        if (self._isSubscriber):
            self._client.unsubscribe(self._topic)
        self._client.loop_stop()
        self._client.disconnect()