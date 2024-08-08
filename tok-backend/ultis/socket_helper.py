from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from api.services.telegram import logging
from apps.notification.models import Notification
from apps.notification.serializers import NotificationSerializer


def send_to_socket(app, name, data):
    channel_layer = get_channel_layer()
    room_group_name = f"{app}_{name}"
    # logging(data)
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": f"{app}.message",
            "message": data,
        }
    )


def send_noti_to_socket_user(user_id, data):
    channel_layer = get_channel_layer()
    room_group_name = f"user_{user_id}"

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": f"user.message",
            "message": data,
        }
    )


def get_socket_data(event, data):
    return {
        'event': event,
        'data': data
    }


def get_socket_data_conversation(event, data, room_id):
    return {
        'event': event,
        'room_id': room_id,
        'data': data
    }


def get_socket_data_livestream(event, data, live_id):
    return {
        'event': event,
        'live_id': live_id,
        'data': data
    }


def join_noti_room(user, request):
    notification = Notification.objects.get_or_create(user=user,
                                                      title_vi='Chào mừng bạn mới',
                                                      body_vi='Chào mừng bạn đến với TOK, cùng trải nghiệm thật nhiều '
                                                              'điều thú vị tại đây nhé.',
                                                      title_en='Welcome',
                                                      body_en="Welcome to TOK, let's experience many interesting things here",
                                                      type='SYSTEM',
                                                      direct_user=None,
                                                      custom_data=None)[0]
    data_serializer = NotificationSerializer(notification, context={'request': request}).data
    send_noti_to_socket_user(str(user.id), get_socket_data('NEW_NOTIFICATION', data_serializer))

