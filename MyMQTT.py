import paho.mqtt.client as PahoMQTT
import json

class MyMQTT:
    def __init__(self, clientID, broker, port, notifier):
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.clientID = clientID
        self._topic = ""
        self._isSubscriber = False
        
        # 1) Create an instance of paho.mqtt.client - client(client_id="", clean_session=True, userdata=None, protocol=MQTTv311)
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived    
        
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
    
    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received
        self.notifier.notify (msg.topic, msg.payload) #do something with the message just received ?

    def start(self):
        #manage connection to broker
        # 2) Connect to a broker - connect(host, port=1883, keepalive=60, bind_address="")
        self._paho_mqtt.connect(self.broker , self.port)
        # 3) Call one of the loop() functions to maintain network traffic flow with the broker
        self._paho_mqtt.loop_start()
       
    def mySubscribe (self, topic):
        # if needed, you can do some computation or error-check before subscribing 
        print ("subscribing to %s" % (topic))
        # 4) Use subscribe() to subscribe to a topic and receive messages - subscribe(topic, qos=0)
        self._paho_mqtt.subscribe(topic, 2)
        # just to remember that it works also as a subscriber
        self._isSubscriber = True
        self._topic = topic
            
    def myPublish (self, topic, msg):
        # if needed, you can do some computation or error-check before publishing
        print ("publishing '%s' with topic '%s'" % (msg, topic))
        # 5) Use publish() to publish messages with a certain topic to the broker - publish(topic, payload=None, qos=0, retain=False)
        self._paho_mqtt.publish(topic, json.dumps(msg), 2)
    
    def unsubscribe(self):
        if (self._isSubscriber):
            # 6) Use unsubscribe() to unsubscribe to a topic before disconnecting (if it is working, also as subscriber)
            self._paho_mqtt.unsubscribe(self._topic)
        
    def stop (self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber
            self._paho_mqtt.unsubscribe(self._topic)
        # 7) Use disconnect() to disconnect from the broker
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()