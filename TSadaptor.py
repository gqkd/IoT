#TS adaptor:
# 1. chiede al box catalog dove si deve iscrivere per i topic dei sensori -> ricorsivo ogni tot sec
# 2. si iscrive ai topic in questione
# 3. manda una request HTTP a thingspeak per cercare se c'è il canale della box
# 4. se non c'è crea il canale per la box in questione
# 5. spedisce i dati in HTTP a thingspeak
from MyMQTT2 import *
class TSadaptor:
    def __init__(self):
        pass
    def 
if __name__ == "__main__":
    ist=TSadaptor()
    # 1.chiedi al box i topic
    ist.topicsearch()