from Sensor_Temperature import *
from Sensor_Acceleration import *
from Sensor_Mass import *
from Sensor_OxygenLevel import *
       
if __name__ == '__main__':
    conf=json.load(open("settings.json"))
    conf2=json.load(open("settingsboxcatalog.json"))
    timesenddata = conf2["timesenddata"]
    topic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]

    #Temperatura:
    temp1 = SensorTemperature("100", "001", topic)

    #Accelerazione:
    acc1 = SensorAcceleration("200","001",topic)

    #Massa:
    mass1 = SensorMass("300","001",topic)

    #Livello di ossigenazione:
    oxy1 = SensorOxygen("400",'001',topic)

    #Connessione al broker
    temp1.start_MyMQTT(broker, port)
    acc1.start_MyMQTT(broker, port)
    mass1.start_MyMQTT(broker, port)
    oxy1.start_MyMQTT(broker, port)

    #Sottoscrizione dei sesori al catalog e invio dei dati campionati:
    temp1.start()
    acc1.start()
    mass1.start()
    oxy1.start()


