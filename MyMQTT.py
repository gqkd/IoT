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
        self._client = mqtt.Client(clientID, True)
        self._client.on_connect = self.myon_connect
        self._client.on_message = self.myon_message
        self.start()

    def myon_connect(self, _client, userdata, flags, rc):
        print ("\n%s Connected to %s with result code: %d\n" % (self.client_id, self.broker, rc))

    
    def start(self):
        try:
            self._client.connect(self.broker, self.port)
        except:
            print("\nNot connected to the broker %s", self.broker)
        self._client.loop_start()
        
    def myPublish(self, topic, msg):
        pubs=self._client.publish(topic, json.dumps(msg), 2)
        if pubs[0]==0:
            pass
        else:
            print("\nMessage NOT published to topic %s" % (topic))

    def myon_message(self, _client, userdata, msg):
        self.notifier.notify (msg.topic, msg.payload)

    def mySubscribe(self, topic):
        subs=self._client.subscribe(topic, 2)
        self._isSubscriber = True
        self._topic = topic
        if subs[0]==0:
            pass
        else:
            print("\n %s NOT subscibed to topic %s\n" % (self.client_id,topic))

    def unsubscribe(self):
        if (self._isSubscriber):
            self._client.unsubscribe(self._topic)
            
    def stop (self):
        if (self._isSubscriber):
            self._client.unsubscribe(self._topic)
        self._client.loop_stop()
        self._client.disconnect()