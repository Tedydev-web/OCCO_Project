# Đọc file JSON vào một dictionary
import json
import re

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.db.models import Q


with open('constants/bad_words.json', 'r', encoding='utf-8') as f:
    banned_words = json.load(f)


class JsonWordValidator(BaseValidator):
    message = 'Đã chứa từ cấm trong các từ bạn nhập'

    def compare(self, value, banned_words):
        # Loại bỏ các ký tự không phải chữ cái và số
        words = value.split()  # Tách từ dựa trên khoảng trắng
        for word in words:
            if word.lower() in banned_words:
                raise ValidationError('Tồn tại nội dung vi phạm qui tắc cộng đồng.', code='invalid')

