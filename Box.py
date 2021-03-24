from Sensor_Temperature import *
from Sensor_Acceleration import *
from Sensor_Mass import *
from Sensor_OxygenLevel import *
from Sensor_GPS import *
from Service_temperatureControl import *
from Service_oxygenControl import *
from Service_accelerationControl import *
from Service_weightControl import *
from Actuator_speaker import *
import requests

if __name__ == '__main__':
    conf=json.load(open("settings.json"))
    conf2=json.load(open("settingsboxcatalog.json"))
    timesenddata = conf2["timesenddata"]
    topic = conf["baseTopic"]
    broker = conf["broker"]
    port = conf["port"]
    #richiesta per il public URL del boxcatalog
    r=requests.get("https://api.thingspeak.com/channels/1333953/fields/1.json?api_key=12YLI1DSAWUJS27X&results=1")
    jsonBody=json.loads(r.text)
    publicURL=jsonBody['feeds'][0]['field1']
    # Temperatura:
    temp1 = SensorTemperature("100", "001", topic, publicURL)
    # Accelerazione:
    acc1 = SensorAcceleration("200","001",topic, publicURL)
    # Massa:
    mass1 = SensorMass("300","001",topic, publicURL)
    # Livello di ossigenazione:
    oxy1 = SensorOxygen("400",'001',topic, publicURL)
    # Speaker
    speak1 = Speaker('500','001',broker,port, publicURL)
    # GPS
    GPS1 = SensorGPS('600','001',port, publicURL)
    # Controllo temperatura
    contTemp1 = TemperatureControl('1',topic,broker,port, publicURL)
    # Controllo accelerazione
    contAcc1 = AccelerationControl('2',topic,broker,port, publicURL)
    # Controllo ossigeno
    contOx1 = OxygenControl('3',topic,broker,port, publicURL)

    contMas1 = WeightControl('4',topic,broker,port, publicURL)
    #Connessione al broker
    temp1.start_MyMQTT(broker, port)
    acc1.start_MyMQTT(broker, port)
    mass1.start_MyMQTT(broker, port)
    oxy1.start_MyMQTT(broker, port)
    GPS1.start_MyMQTT(broker, port)

    #Sottoscrizione dei sesori al catalog e invio dei dati campionati:
    temp1.start()
    acc1.start()
    mass1.start()
    oxy1.start()
    GPS1.start()
    speak1.start()
    contTemp1.start()
    contOx1.start()
    contAcc1.start()
    contMas1.start()

   


