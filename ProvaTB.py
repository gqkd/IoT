import requests
import random
import time
import json

url="https://demo.thingsboard.io/api/v1/LtSJM5BfGXEwB4NTjjho/telemetry"
header={'Content-Type':'application/json'}
for i in range(50):
    n=random.randint(15,40)
    print(n)
    payload={'sensor_ID':1,'temperature':n}
    r = requests.post(url, data=json.dumps(payload), headers=header)
    print(r,r.text, r.status_code)
    time.sleep(10)