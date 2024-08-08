from celery import shared_task
from django.db import transaction
from django.db.models import Q
from django.test import RequestFactory

from api.services.firebase import send_not_save_notification
from api.services.telegram import logging
from apps.conversation.models import Room, Message, SeenByMessage
from apps.conversation.serializers import RoomUserBasicSerializer, MessageSerializer, RoomSerializer, \
    LastMessageSerializer
from apps.user.models import CustomUser
from ultis.socket_helper import send_to_socket, get_socket_data_conversation, send_noti_to_socket_user, get_socket_data


@shared_task
def send_event_to_socket_users_in_room(room_id, event):
    room = Room.objects.get(id=room_id)
    room_users = room.roomuser_set.select_related('user').all()
    data = RoomUserBasicSerializer(room_users, many=True).data

    for roomuser in room_users:
        id = roomuser.user.id
        send_to_socket('conversation', str(id),
                       get_socket_data_conversation(event, data, room_id=str(room_id)))


@shared_task
def send_group_to_socket_users_in_room(room_id, event, user_id):
    room = Room.objects.get(id=room_id)
    room_users = room.roomuser_set.select_related('user').all()
    request_factory = RequestFactory()
    request = request_factory.get('/')
    request.user = CustomUser.objects.get(id=user_id)
    data = RoomSerializer(room, context={'request': request}).data
    for roomuser in room_users:
        id = roomuser.user.id
        send_to_socket('conversation', str(id),
                       get_socket_data_conversation(event, data, room_id=str(room_id)))


@shared_task
def send_block_event_to_socket_users(from_user, to_user, event):
    room = Room.objects.filter(
        Q(roomuser__user__id=to_user) &
        Q(type='CONNECT')).filter(
        Q(roomuser__user__id=from_user)
    ).first()
    request_factory = RequestFactory()
    room_users = room.roomuser_set.select_related('user').all()

    for roomuser in room_users:
        request = request_factory.get('/')
        request.user = roomuser.user
        data = RoomSerializer(room, context={'request': request}).data
        send_to_socket('conversation', str(roomuser.user.id),
                       get_socket_data_conversation(event, data, room_id=str(room.id)))

    send_noti_to_socket_user(str(to_user), get_socket_data(event, str(room.id)))


@shared_task
def send_message_to_socket_users_in_room(room_id, list_msg):
    messages = Message.objects.filter(id__in=list_msg)
    serializers = MessageSerializer(messages, many=True).data
    room = Room.objects.get(id=room_id)
    room_users = room.roomuser_set.select_related('user').all()
    for data in serializers:
        for roomuser in room_users:
            send_to_socket('conversation', str(roomuser.user.id),
                           get_socket_data_conversation('NEW_MESSAGE', data, room_id=str(room.id)))


@shared_task
def send_new_message_to_room(room_id, msg_id, user_id):
    sender = CustomUser.objects.get(id=user_id)

    msg = Message.objects.get(id=msg_id)
    data_msg = MessageSerializer(msg).data

    room = Room.objects.get(id=room_id)
    request_factory = RequestFactory()
    request = request_factory.get('/')
    request.user = sender
    data_room = RoomSerializer(room, context={'request': request}).data

    rs = room.roomuser_set.select_related('user').all()
    rs.update(date_removed=None)

    if room.type == 'PRIVATE':
        data_msg['sender']['full_name'] = data_room['name']
        data_msg['sender']['avatar'] = data_room['image']

    for r in rs:
        last_msg = LastMessageSerializer(msg, context={'user': r.user}).data
        r.set_last_message(last_msg)
        # data_msg['text'] = last_msg['text']
        data_room['last_message'] = last_msg

        if r.user != sender:
            full_name = sender.full_name
            if room.type == 'PRIVATE':
                full_name = data_room['name']
            if msg.type not in ['CALL', 'VIDEO_CALL', 'GIFT']:
                if r.notification_mode == 'on':
                    send_not_save_notification(user=r.user,
                                               title=full_name,
                                               body=last_msg['text'],
                                               custom_data={
                                                   "direct_type": "message_coming"
                                               })
        else:
            r.reset_total_unseen()

        if room.newest_at is None:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_CONVERSATION', data_room, room_id=str(room.id)))

        if r.is_removed:
            r.is_removed = False
            r.save()
            if r.notification_mode == 'on':
                send_to_socket('conversation', str(r.user.id),
                               get_socket_data_conversation('NEW_CONVERSATION', data_room, room_id=str(room.id)))
        else:
            if r.notification_mode == 'on':
                send_to_socket('conversation', str(r.user.id),
                               get_socket_data_conversation('NEW_MESSAGE', data_msg, room_id=str(room.id)))

        if r.user != sender:
            r.set_total_unseen()

    room.set_newest()


@shared_task
def update_seen_message(user_id, room_id):
    user = CustomUser.objects.get(id=user_id)
    room = Room.objects.get(id=room_id)
    messages_unseen = Message.objects.filter(room=room,
                                             seenbymessage__isnull=True).filter(seenbymessage__user__isnull=True)
    rs = room.roomuser_set.select_related('user').all()
    request_factory = RequestFactory()
    request = request_factory.get('/')
    request.user = user
    for message in messages_unseen:
        SeenByMessage.objects.create(user=user, message=message)
        data_msg = MessageSerializer(message, context={'request': request}).data
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_SEEN_MSG', data_msg, room_id=str(room.id)))


@shared_task
def chk_and_update_seen_message(user_id, room_id):
    user = CustomUser.objects.get(id=user_id)
    room = Room.objects.get(id=room_id)
    messages_unseen = Message.objects.filter(room=room,
                                             seenbymessage__isnull=True).filter(seenbymessage__user__isnull=True)

    rs = room.roomuser_set.select_related('user').all()
    request_factory = RequestFactory()
    request = request_factory.get('/')
    request.user = user
    for message in messages_unseen:
        SeenByMessage.objects.create(user=user, message=message)
        data_msg = MessageSerializer(message, context={'request': request}).data
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_SEEN_MSG', data_msg, room_id=str(room.id)))
