import json
import os

from django.core.management.base import BaseCommand

from apps.general.models import DevSetting, AppConfig, DefaultAvatar
from apps.user.models import WorkInformation, SearchInformation, HobbyInformation, CommunicateInformation, \
    CharacterInformation
from ultis.config_helper import upload_default_avatar, upload_dev_settings, upload_app_config, \
    upload_country_images_to_minio, upload_gift_default, upload_emoji_default, upload_banking


class Command(BaseCommand):
    help = 'Load information model'

    def handle(self, *args, **options):
        try:
            # Add information data
            with open('constants/informationData.json', encoding='utf-8') as file:
                data = json.load(file)

                # Thêm dữ liệu vào các model
                for category, values in data.items():
                    model_class = self.get_model_class(category)
                    if model_class:
                        for item in values:
                            model_class.objects.get_or_create(**item)
                print("Information loaded successfully.")

            # Add dev setting
            # upload_dev_settings()

            # Add app config
            # upload_app_config()

            # Default Avatar
            # upload_default_avatar(self)

            # Countries Images
            # upload_country_images_to_minio()

            # Default gift
            # upload_gift_default()

            # Default emoji
            # upload_emoji_default()

            #Upload banking
            upload_banking()
        except Exception as e:
            print(f"Error loading Information: {str(e)}")

    def get_model_class(self, category):
        model_mapping = {
            "work_information": WorkInformation,
            "character_information": CharacterInformation,
            "search_information": SearchInformation,
            "hobby_information": HobbyInformation,
            "communicate_information": CommunicateInformation
        }
        return model_mapping.get(category)
