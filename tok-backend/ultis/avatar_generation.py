from apps.user.models import LetterAvatar
import requests
from django.db import models
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from ultis.helper import convert_unicode_text


def get_default_avatar(avatar, full_name, phone_number):
    full_name = convert_unicode_text(full_name)
    if not avatar:
        input_text = ""
        if len(full_name):
            if " " in full_name:
                words = full_name.split(" ")
                if len(words):
                    if len(words) > 1:
                        input_text = str(words[-2][0]).upper() + str(words[-1][0]).upper()
                    else:
                        input_text = str(words[0][0]).upper()
            else:
                input_text = str(full_name[0]).upper()

        if input_text.strip() == '' or input_text.strip() == '+':
            if len(phone_number):
                input_text += str(phone_number[-2:]).upper()
            else:
                input_text = 'N'

        bg = 'D1E0FF'
        color = 'fff'
        bold = 'true'
        size = '128'

        url = f'https://ui-avatars.com/api/?background={bg}&color={color}&format=png&bold={bold}&size={size}&name={input_text}'

        check = LetterAvatar.objects.filter(name=input_text).exists()
        if check:
            return LetterAvatar.objects.filter(name=input_text).first().image.url

        letter_avatar, _ = LetterAvatar.objects.get_or_create(
            name=input_text,
        )
        if not letter_avatar.image:
            letter_avatar.image.save(f"{input_text}_avatar.png", get_image_file_from_url(url))
            print('Downloaded', input_text)

        return letter_avatar.image.url

    return avatar


def get_image_file_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        img_temp = NamedTemporaryFile()
        # img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.content)
        img_temp.flush()
        return File(img_temp)
