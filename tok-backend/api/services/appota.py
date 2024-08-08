import base64
import hashlib
import hmac
import json
import urllib
import uuid
from datetime import datetime, timedelta

import jwt
import requests


def hmac_sha256(data: bytes, secret_key: bytes) -> bytes:
    """
    Tính toán giá trị HMAC-SHA256 của dữ liệu đầu vào với khóa bí mật.

    :param data: Dữ liệu đầu vào dưới dạng bytes.
    :param secret_key: Khóa bí mật để mã hóa dưới dạng bytes.
    :return: Giá trị HMAC-SHA256 dưới dạng bytes.
    """
    hmac_object = hmac.new(secret_key, data, hashlib.sha256)
    return hmac_object.digest()


def base64_decode(encoded_data: str) -> bytes:
    """
    Giải mã dữ liệu từ định dạng Base64.

    :param encoded_data: Dữ liệu được mã hóa bằng Base64 dưới dạng chuỗi.
    :return: Dữ liệu đã giải mã dưới dạng bytes.
    """
    return base64.b64decode(encoded_data)


def json_decode(json_data: bytes) -> dict:
    """
    Giải mã dữ liệu JSON từ dạng bytes.

    :param json_data: Dữ liệu JSON ở dạng bytes.
    :return: Dữ liệu đã giải mã dưới dạng dict (hoặc list nếu dữ liệu là danh sách JSON).
    """
    json_string = json_data.decode('utf-8')
    return json.loads(json_string)


def decode_result_data(encoded_data: str) -> dict:
    """
    Giải mã dữ liệu được mã hóa bằng Base64 và chứa JSON.

    :param encoded_data: Dữ liệu được mã hóa bằng Base64 và chứa JSON dưới dạng chuỗi.
    :return: Dữ liệu đã giải mã dưới dạng dict (hoặc list nếu dữ liệu là danh sách JSON).
    """
    json_bytes = base64_decode(encoded_data)
    return json_decode(json_bytes)


def get_uuid_v4() -> str:
    """
    Tạo UUID phiên bản 4.

    :return: UUID phiên bản 4 dưới dạng chuỗi.
    """
    unique_id = uuid.uuid4()
    return str(unique_id)


class AppotaService:
    """
    Class dịch vụ của Appota, cung cấp các phương thức để tạo chữ ký, tạo JWT, và giải mã dữ liệu.
    """

    def __init__(self):
        """
        Khởi tạo đối tượng AppotaService với các thông tin cần thiết.
        """
        self.partner_code = 'CYDEVA'
        self.api_key = '1KuFdPnwjQCTZcxOKK3IHkUtcrpay4z5'
        self.secret_key = 'Gx5COnulEs3nTygUESNMbPwxu2a7P4pu'
        self.algorithm = 'HS256'
        self.api_version = 'v2'
        self.url = f'https://payment.dev.appotapay.com/api/{self.api_version}'
        self.headers = {
            'Content-Type': 'application/json',
            'X-APPOTAPAY-AUTH': self.get_jwt_token(),
            'X-Language': 'vi',
        }

    def get_jwt_token(self) -> str:
        """
        Tạo mã thông báo JWT với thời hạn 7 ngày.

        :return: Mã thông báo JWT dưới dạng chuỗi.
        """
        expiration_time = int((datetime.now() + timedelta(days=7)).timestamp())
        headers = {
            "typ": "JWT",
            "alg": self.algorithm,
            "cty": "appotapay-api;v=1"
        }
        payload = {
            "iss": self.partner_code,
            "jti": f"{self.api_key}-{expiration_time}",
            "api_key": self.api_key,
            "exp": expiration_time
        }
        token = jwt.encode(
            payload=payload,
            key=self.secret_key,
            algorithm=self.algorithm,
            headers=headers
        )
        return token

    def generate_signature(self, params):
        """
        Tạo chữ ký HMAC-SHA256 từ các tham số và secret key.

        :param params: Dictionary chứa các tham số để tạo chữ ký.
        :param secret_key: Secret key để tính toán HMAC-SHA256.
        :return: Chuỗi chữ ký.
        """
        # Sắp xếp các tham số theo thứ tự alphabet của khóa
        # sorted_params = sorted(params.items())
        #
        # # Tạo chuỗi kết hợp từ các tham số đã sắp xếp
        # param_string = '&'.join(f"{key}={urllib.parse.quote(str(value), safe='')}" for key, value in sorted_params)

        # Tạo chữ ký HMAC-SHA256
        signature = hmac.new(
            key=self.secret_key.encode('utf-8'),
            msg=params.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()

        return signature

    def create_order(self, transaction):
        url = f"{self.url}/orders/payment"

        noti_url = 'https://occo.tokvn.live/api/v1/payment/appota/returnURL/'

        data = {
            "transaction": {
                "amount": transaction.amount,
                "currency": "VND",
                "paymentMethod": "ALL",
                "action": "PAY",
                "bankCode": ""

        },
            "partnerReference": {
                "order": {
                    "id": str(transaction.id),
                    "info": transaction.get_transaction_type_display(),
                    "extraData": ""
                },
                "notificationConfig": {
                    "notifyUrl": noti_url,
                    "redirectUrl": noti_url,
                    "installmentNotifyUrl": noti_url
                }
            }
        }

        payload = json.dumps(data)
        response = requests.request("POST", url, headers=self.headers, data=payload)

        data = json.loads(response.text)
        return data

    def get_order(self, order_id):
        url = f"{self.url}/orders/transaction"
        data = {
            "referenceId": order_id,
            "type": "PARTNER_ORDER_ID"
        }
        payload = json.dumps(data)

        response = requests.request("GET", url, headers=self.headers, data=payload)

        data = json.loads(response.text)

        return data


