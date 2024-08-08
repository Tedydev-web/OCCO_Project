import requests
from rest_framework.exceptions import ValidationError

from api.services.telegram import logging


def nsfw_image_validator(image):
    url = "https://ai.cydeva.tech/api/v1/nsfw/check/"
    payload = {'key': '123123'}

    files = [
        ('image', (image.name, image.file, image.content_type))
    ]

    headers = {}

    response = requests.request("POST", url, headers=headers, data=payload, files=files)

    if response.status_code != 200:
        logging("Server NSFW Error")
    else:
        response_data = response.json()

        # Bạn cần thay đổi logic kiểm tra này dựa trên cấu trúc của response_data
        status_code = response_data.get('status_code', 200)
        if status_code != 200:
            logging(response_data)
            raise ValidationError("Ảnh chứa nội dung vi phạm tiêu chuẩn cộng đồng.")

