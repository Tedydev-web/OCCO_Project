import time
from datetime import datetime

import jwt
from google.auth.transport import requests as google_requests
from google.oauth2 import service_account
from oauth2client.service_account import ServiceAccountCredentials

from api.services.telegram import logging


def get_access_token():
    data = {
        'client_id': '848038516510-3s4kq6pe5v0710ad52as4qf10h53v7aa.apps.googleusercontent.com',
        'grant_type': 'client_credentials'
    }

    # Gửi yêu cầu POST để lấy Access Token
    response = requests.post('https://oauth2.googleapis.com/token', data=data)
    print(response)
    # Kiểm tra nếu yêu cầu thành công
    if response.status_code == 200:
        # Trả về Access Token từ dữ liệu JSON của phản hồi
        return response.json()['access_token']
    else:
        # In lỗi nếu yêu cầu không thành công
        print("Lỗi:", response.status_code)
        return None


import requests

CREDENTIAL_SCOPES = ["https://www.googleapis.com/auth/androidpublisher"]
CREDENTIALS_KEY_PATH = 'app-lua-defa5194c6cf.json'
import time


def get_service_account_token():
    try:
        access_token = ServiceAccountCredentials.from_json_keyfile_name(
            CREDENTIALS_KEY_PATH, CREDENTIAL_SCOPES).get_access_token().access_token

        return access_token
    except Exception as e:
        print("Lỗi khi lấy access token:", e)
        return None


def get_data_from_api(package_name, product_id, token, access_token):
    url = f"https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package_name}/purchases/products/{product_id}/tokens/{token}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Data lấy được từ API
        data = response.json()
        return data
    else:
        # Xử lý lỗi nếu có
        logging(f"Xảy ra lỗi trong quá trình lấy thêm data: {response.status_code} {response.text}")
        return None
