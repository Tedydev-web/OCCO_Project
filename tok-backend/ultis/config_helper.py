import os
import json
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.images import ImageFile
from minio import Minio, S3Error

from apps.discovery.models import Gift, Emoji
from apps.general.models import DefaultAvatar, AppConfig, DevSetting
from apps.payment.models import Banking
from apps.user.models import WorkInformation, CharacterInformation, SearchInformation, HobbyInformation, \
    CommunicateInformation
from core.settings import *

minioClient = Minio(endpoint=AWS_S3_ENDPOINT_URL.replace('https://', ''),
                    access_key=AWS_ACCESS_KEY_ID,
                    secret_key=AWS_SECRET_ACCESS_KEY,
                    secure=True)


def upload_country_images_to_minio():
    def clean_url(url):
        parsed_url = urlparse(url)
        return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

    # Đọc dữ liệu từ tệp JSON
    with open('constants/countryNstate.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Lặp qua từng quốc gia trong dữ liệu và tải ảnh lên MinIO
    for country in data:
        # Lấy tên quốc gia và iso2 code
        country_name = country["name"]
        iso2_code = country["iso2"]
        image_path = os.path.join("ultis", "country_images", f"{iso2_code}.png")

        # Kiểm tra xem tệp ảnh tồn tại
        if os.path.exists(image_path):
            try:
                minioClient.stat_object(AWS_STORAGE_BUCKET_NAME, f"assets/countriesImage/{iso2_code}.png")
            except S3Error as err:
                if err.code == "NoSuchKey":
                    try:
                        # Tải ảnh lên MinIO
                        minioClient.fput_object(AWS_STORAGE_BUCKET_NAME,
                                                f"assets/countriesImage/{iso2_code}.png",
                                                image_path,
                                                content_type="image/png",  # Loại nội dung của tệp
                                                metadata={"Content-Disposition": "inline"})

                        # Lấy URL sạch mà không có các tham số truy vấn
                        clean_image_url = clean_url(minioClient.presigned_get_object(AWS_STORAGE_BUCKET_NAME,
                                                                                     f"assets/countriesImage/{iso2_code}.png"))

                        # Cập nhật giá trị của key "flag" trong tệp JSON với URL sạch
                        country["flag"] = clean_image_url
                        print("Success", iso2_code)
                    except S3Error as err:
                        print(f"Error uploading {iso2_code}.png to MinIO: {err}")
        else:
            print(f"Image file for {country_name} not found.")

    # Ghi dữ liệu đã cập nhật vào tệp JSON
    with open('constants/countryNstate.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def upload_default_avatar(self):
    default_avatar_path = 'constants/default_images/default_avatar.png'
    default_notification_path = 'constants/default_images/notification.png'
    default_anonymous_path = 'constants/default_images/anonymous.png'
    default_random_path = 'constants/default_images/random.png'

    # Avatar
    if not DefaultAvatar.objects.filter(key='avatar').exists():
        default_avatar = DefaultAvatar.objects.create(key='avatar')
        default_avatar.image.save(os.path.basename(default_avatar_path), open(default_avatar_path, 'rb'))
        self.stdout.write(self.style.SUCCESS('Default avatar added successfully.'))
    else:
        self.stdout.write(self.style.WARNING('Default avatar already exists.'))

    # Notification
    if not DefaultAvatar.objects.filter(key='notification').exists():
        default_avatar = DefaultAvatar.objects.create(key='notification')
        default_avatar.image.save(os.path.basename(default_notification_path), open(default_notification_path, 'rb'))
        self.stdout.write(self.style.SUCCESS('Default notification added successfully.'))
    else:
        self.stdout.write(self.style.WARNING('Default notification already exists.'))

    # Anonymous
    if not DefaultAvatar.objects.filter(key='anonymous').exists():
        default_avatar = DefaultAvatar.objects.create(key='anonymous')
        default_avatar.image.save(os.path.basename(default_anonymous_path), open(default_anonymous_path, 'rb'))
        self.stdout.write(self.style.SUCCESS('Default anonymous added successfully.'))
    else:
        self.stdout.write(self.style.WARNING('Default anonymous already exists.'))

    # Random
    if not DefaultAvatar.objects.filter(key='random').exists():
        default_avatar = DefaultAvatar.objects.create(key='random')
        default_avatar.image.save(os.path.basename(default_random_path), open(default_random_path, 'rb'))
        self.stdout.write(self.style.SUCCESS('Default random added successfully.'))
    else:
        self.stdout.write(self.style.WARNING('Default random already exists.'))


def upload_app_config():
    with open('constants/appConfig.json', encoding='utf-8') as file:
        data = json.load(file)

        # Thêm dữ liệu vào mô hình DevSetting
        # Tạo hoặc cập nhật mỗi cặp key-value trong AppConfig model
        for key, value in data.items():
            app_config, created = AppConfig.objects.get_or_create(key=key)
            if created:
                app_config.value = value
                app_config.save()
        print("Appconfig created successfully.")


def upload_dev_settings():
    with open('constants/devSettings.json', encoding='utf-8') as file:
        data = json.load(file)

        # Thêm dữ liệu vào mô hình DevSetting
        dev_setting, created = DevSetting.objects.get_or_create(pk=1)
        if created:
            dev_setting.config = data
            dev_setting.save()
            print("DevSetting created successfully.")


def upload_gift_default():
    with open('constants/gift.json', encoding='utf-8') as file:
        data = json.load(file)
        for gift_id, gift_data in data.items():
            # Tải hình ảnh từ đường dẫn trong tệp JSON
            with open(gift_data['image'], 'rb') as image_file:
                image_data = image_file.read()
            # Tạo một đối tượng File của Django từ dữ liệu hình ảnh
            image_name = gift_data['image'].split('/')[-1]  # Lấy tên file từ đường dẫn
            django_file = ContentFile(image_data, name=image_name)
            # Tạo đối tượng Gift và lưu vào cơ sở dữ liệu
            gift, created = Gift.objects.get_or_create(
                title_vi=gift_data['title_vi'],
                title_en=gift_data['title_en'],
                type=gift_data['type'],
                price=gift_data['price']
            )
            if created:
                gift.image = ImageFile(django_file)
                gift.save()
                print('Success upload gift')


def upload_emoji_default():
    with open('constants/emoji.json', encoding='utf-8') as file:
        data = json.load(file)
        for emoji_id, emoji_data in data.items():
            # Tải hình ảnh từ đường dẫn trong tệp JSON
            with open(emoji_data['image'], 'rb') as image_file:
                image_data = image_file.read()
            # Tạo một đối tượng File của Django từ dữ liệu hình ảnh
            image_name = emoji_data['image'].split('/')[-1]  # Lấy tên file từ đường dẫn
            django_file = ContentFile(image_data, name=image_name)
            # Tạo đối tượng emoji và lưu vào cơ sở dữ liệu

            emoji, created = Emoji.objects.get_or_create(name=image_name)
            if created:
                emoji.image = ImageFile(django_file)
                emoji.save()
                print('Success upload emoji')


def upload_banking():
    if Banking.objects.count() != 0:
        return 0
    with open('constants/banks.json', encoding='utf-8') as file:
        bank_json = json.load(file)
        for key, values in bank_json.items():
                url = urlparse(str(values['bankLogoUrl']))
                filename = os.path.basename(url.path)
                try:
                    b, created = Banking.objects.get_or_create(fullname=values['name'],
                                                               short_name=values['shortName'],
                                                               filename=filename,
                                                               is_viet_pr=values['isVietQr'],
                                                               is_napas=values['isNapas'],
                                                               is_disburse=values['isDisburse'],
                                                               bin_card=values['bin'],
                                                               bank_code=key)
                    response = requests.get(values['bankLogoUrl'])
                    b.icon.save(filename, ContentFile(response.content), save=True)

                    if created:
                        print(f"Success add {b.fullname} {b.bank_code}")
                except Exception as ex:
                    print(ex)
