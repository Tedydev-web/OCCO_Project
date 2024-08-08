import datetime

from firebase_admin import messaging

import firebase_admin
from firebase_admin import credentials

from apps.notification.models import UserDevice, Notification
from apps.notification.serializers import NotificationSerializer
from ultis.socket_helper import get_socket_data, send_to_socket, send_noti_to_socket_user

try:
    cred = credentials.Certificate("serviceAccountTOK.json")
    firebase_admin.initialize_app(cred, name="TOK")
except:
    ...


def send_push_notification(device_token, title, body, custom_data=None, app_name='TOK'):
    try:
        app = firebase_admin.get_app(app_name)

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=device_token,
            data=custom_data,
        )
        response = messaging.send(message, app=app)
        print(f"Successfully sent message to {app_name}:", response)
    except Exception as e:
        print(f"Error sending message to {app_name}:", str(e))


def send_push_notification_bulk(device_tokens, title, body, custom_data=None, app_name='TOK'):
    try:
        app = firebase_admin.get_app(app_name)

        messages = [messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=device_token,
            data=custom_data,
        ) for device_token in device_tokens]

        response = messaging.send_all(messages, app=app)
        print(f"Successfully sent messages to {app_name}:", response)
    except Exception as e:
        print(f"Error sending messages to {app_name}:", str(e))


def send_and_save_notification(user, title='', body='', direct_type='', direct_value='', direct_user=None,
                               custom_data=None,
                               app_name='TOK', type_noti='SYSTEM'):
    try:
        app = firebase_admin.get_app(app_name)
        notification = Notification(user=user,
                                    title_vi=title,
                                    body_vi=body,
                                    direct_type=direct_type,
                                    direct_value=direct_value,
                                    direct_user=direct_user,
                                    custom_data=custom_data,
                                    type=type_noti)
        notification.save()
        # Check user's notification mode
        if user.notification_mode == 'off':
            return  # Do not send notification

        elif user.notification_mode == 'off23to6':
            current_time = datetime.datetime.now().time()
            if current_time >= datetime.time(23, 0) or current_time <= datetime.time(6, 0):
                return  # Do not send notification during this period

        # If notification_mode is 'on', proceed with sending notification
        devices = UserDevice.objects.filter(user=user)
        if devices.exists():
            device_tokens = [x.token for x in devices]
            send_push_notification_bulk(device_tokens, title, body, custom_data=custom_data, app_name=app_name)

        return notification

    except Exception as e:
        print(f"Error in {app_name}:", str(e))


def send_not_save_notification(user, body, title='', custom_data=None, app_name='TOK'):
    try:
        app = firebase_admin.get_app(app_name)
        # Check user's notification mode
        if user.notification_mode == 'off':
            return  # Do not send notification

        elif user.notification_mode == 'off23to6':
            current_time = datetime.datetime.now().time()
            if current_time >= datetime.time(23, 0) or current_time <= datetime.time(6, 0):
                return  # Do not send notification during this period
        devices = UserDevice.objects.filter(user=user)
        if devices.exists():
            device_tokens = [x.token for x in devices]
            send_push_notification_bulk(device_tokens, title, body, custom_data=custom_data, app_name=app_name)

    except Exception as e:
        print(f"Error in {app_name}:", str(e))


def send_and_save_admin_notification(user, title, body, direct_type, direct_value, request, direct_user,
                                     custom_data=None,
                                     app_name='TOK'):
    try:

        notification = Notification.objects.create(user=user,
                                                   title_vi=title[0],
                                                   body_vi=body[0],
                                                   title_en=title[1],
                                                   body_en=body[1],
                                                   type='SYSTEM',
                                                   direct_user=None,
                                                   custom_data=custom_data
                                                   )
        data_serializer = NotificationSerializer(notification).data

        # send_noti_to_socket_user(str(user.id), get_socket_data('NEW_NOTIFICATION', data_serializer))

        app = firebase_admin.get_app(app_name)

        devices = UserDevice.objects.filter(user=user)
        if devices.exists():
            device_tokens = [x.token for x in devices]
            send_push_notification_bulk(device_tokens, title[0], body[0], custom_data=custom_data, app_name=app_name)

    except Exception as e:
        print(f"Error in {app_name}:", str(e))
