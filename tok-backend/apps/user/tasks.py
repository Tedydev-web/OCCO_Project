import datetime

from django.db.models import Q

from apps.conversation.models import Room
from apps.discovery.models import LiveStreamingHistory, LiveUser
from apps.general.models import DevSetting
from apps.user.models import CustomUser, Follow, FriendShip
from celery import shared_task, group

from ultis.socket_helper import send_noti_to_socket_user, get_socket_data, send_to_socket, get_socket_data_livestream


@shared_task
def send_noti_online_to_friend(user_id):
    user = CustomUser.objects.get(id=user_id)
    user_data = {
        'id': str(user.id),
        'full_name': user.full_name,
        'avatar': user.get_avatar
    }  # Assuming user_data is required

    # Lọc ra các object có sender trùng với receiver của các object khác
    fs = CustomUser.custom_objects.list_friend(user).values_list('id', flat=True)
    for uid in fs:
        send_noti_to_socket_user(str(uid), get_socket_data('NEW_ONLINE', user_data))


@shared_task
def send_message_to_user(user_id, live_id, data, event):
    send_to_socket(app='discovery',
                   name=str(user_id),
                   data=get_socket_data_livestream(event=event, data=data, live_id=live_id))


@shared_task
def remove_private_chat_5_hours_inactive(user_id):
    user = CustomUser.objects.get(id=user_id)
    now = datetime.datetime.now()
    five_hours_ago = now - datetime.timedelta(hours=int(DevSetting.get_value('time_remove_private')))
    room_privates = Room.objects.filter(type='PRIVATE', newest_at__lt=five_hours_ago,
                                        roomuser__user=user)
    room_privates.delete()

    live = LiveStreamingHistory.objects.filter(host__id=user_id,
                                               is_stopped=False,
                                               type='STREAM').update(is_stopped=True).first()
    live_id = str(live.id)
    # all_users = LiveUser.objects.select_related('live_streaming').filter(live_streaming__id=live_id)
    all_users = CustomUser.objects.filter(is_fake=False, is_online=True)

    tasks = group(
        send_message_to_user.s(str(user.id), live_id, {}, event='LIVE_ENDED') for user in all_users)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def remove_relation_ship(to_user, from_user):
    Follow.objects.filter(to_user__id=to_user, from_user__id=from_user).delete()
    Follow.objects.filter(from_user__id=to_user, to_user__id=from_user).delete()
    FriendShip.objects.filter(Q(sender__id=to_user, receiver__id=from_user) |
                              Q(sender__id=from_user, receiver__id=to_user)).delete()


@shared_task
def remove_relation_ship_sender(to_user, from_user):
    Follow.objects.filter(to_user__id=to_user, from_user__id=from_user).delete()


@shared_task
def delete_account(user_id):
    user = CustomUser.objects.get(id=user_id)
    friends = CustomUser.custom_objects.list_friend(user)
    user.delete()

    for friend in friends:
        friend.remove_relationship(user_id)
