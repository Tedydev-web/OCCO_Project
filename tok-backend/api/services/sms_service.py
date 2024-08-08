import json
import threading

import requests

from apps.general.models import OTPRequest
from core.settings import OTP_PROVIDER_ID, ZALO_OTP_URL


def process_sms(phone_number, otp):
    otp_request = OTPRequest.objects.create(phone_number=phone_number, otp=otp, return_code="02")

    try:
        payload = json.dumps({
            "phone_number": phone_number,
            "otp": otp,
            "provider": OTP_PROVIDER_ID
        })

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", ZALO_OTP_URL, headers=headers, data=payload)
        data = json.loads(response.text)
        otp_request.return_code = "00" if data['status_code'] == 200 else "01"
        otp_request.info = data['message']
        otp_request.save()

        return response.text
    except Exception as e:
        otp_request.return_code = "03"
        otp_request.info = str(e)
        otp_request.save()
        return str(e)


def send_otp_zalo(phone_number, otp):
    thread = threading.Thread(target=process_sms, args=(phone_number, otp))
    thread.daemon = True
    thread.start()
