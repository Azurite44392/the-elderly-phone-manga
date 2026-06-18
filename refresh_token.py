import requests
import time

while True:
    time.sleep(1500)
    try:
        requests.get("http://127.0.0.1:5025/webhook/update_token")
    except:
        pass
