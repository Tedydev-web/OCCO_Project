import json

import requests
from celery import shared_task
from celery.beat import logger
from django.db.models import Q

from api.services.telegram import logging
from apps.dashboard.models import NotificationAdmin
from apps.general.models import DevSetting
from apps.user.models import CustomUser
from ultis.socket_helper import send_to_socket, get_socket_data


def send_socket_admin(data, country, notification_admin_id):
    if notification_admin_id:
        try:
            notification_admin = NotificationAdmin.objects.get(id=notification_admin_id)
            country = notification_admin.from_user

            custom_data = {
                "title": str(notification_admin.title),
                "body": str(notification_admin.body),
                "type": str(notification_admin.type),
                "created_at": str(notification_admin.created_at.strftime("%d/%m/%Y %H:%M")),
                "link": str(notification_admin.link)
            }
            users_admin = CustomUser.objects.filter(Q(is_superuser=True) &
                                                    (Q(country=country) | Q(country='All'))
                                                    )
            socket_data = get_socket_data('NEW_ADMIN_NOTIFICATION', custom_data)

            for user in users_admin:
                notification_admin.admin_user = user
                notification_admin.save()
                send_to_socket("admin", str(user.id), socket_data)
        except Exception as e:
            logging(msg=f'Lỗi khi gửi thông báo cho admin dashboard từ socket: {e}')

    else:

        socket_data = get_socket_data('NEW_ADMIN_NOTIFICATION', data)
        users_admin = CustomUser.objects.filter(Q(is_staff=True) &
                                                (Q(country=country) | Q(country='All'))
                                                )
        for user in users_admin:
            send_to_socket("admin", str(user.id), socket_data)


@shared_task
def send_telegram_message(message='', user_country='All', notification_admin=None):
    chat_id = DevSetting.get_value('telegramChatID')
    token = DevSetting.get_value('tokenBotTelegram')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': str(chat_id),
        'text': str(message),
        'parse_mode': 'HTML'  # Optional: HTML formatting
    }
    # logger.info(f'notification_admin_id {notification_admin}')
    send_socket_admin(payload, user_country, notification_admin_id=notification_admin)
    response = requests.post(url, data=payload)
    return response
