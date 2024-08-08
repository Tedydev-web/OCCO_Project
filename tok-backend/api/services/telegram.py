import threading
import requests
import json


def logging(msg, addr='', level='DEBUG', active=True):
    def job(msg, addr, level, active):
        app_name = 'TOK'
        try:

            if not active:
                return

            url = "https://www.core.cydeva.tech/api/v1/notification/log/"

            payload = json.dumps({
                "log_level": level,
                "app_name": app_name,
                "message": str(msg)[:500],
                "more_info": str(addr)[:3500]
            })
            headers = {
                'Content-Type': 'application/json',
            }

            requests.request("POST", url, headers=headers, data=payload)
        except:
            ...

    thread = threading.Thread(target=job, args=(msg, addr, level, active))
    thread.start()


