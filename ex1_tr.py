import requests
import time
import threading


hosts = ["http://yahoo.com", "http://google.com", "http://amazon.com",
"http://ibm.com", "http://apple.com", "https://www.microsoft.com", "https://www.youtube.com/", "https://www.polito.it/", "http://www.wikipedia.org", "https://www.reddit.com/", "https://www.adobe.com/", "https://wordpress.org/", "https://github.com/", "https://www.google.com/maps/"]


class MyThread(threading.Thread):
    def __init__(self, threadID, host):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.host = host

    def run(self):
        url = requests.get(self.host)

if __name__=="__main__":
    start=time.time()
    for url in hosts:
        url = requests.get(url)
    stop=time.time()
    print(f" for-cycle: {stop-start} s")

    threads=[]

    for i,url in enumerate(hosts):
        threads.append(MyThread(i,url))
    
    start=time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    stop=time.time()

    print(f" threads: {stop-start} s")