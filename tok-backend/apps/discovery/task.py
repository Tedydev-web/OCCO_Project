from celery import shared_task, group

from api.services.telegram import logging
from apps.discovery.models import LiveUser, MessageLive, LiveStreamingHistory, EmojiLog, GiftLog
from apps.discovery.serializers import MessageLiveSerializer, LiveUserSerializer, LiveStreamingSerializer, \
    EmojiLogSerializer, GiftLogSerializer
from apps.user.models import CustomUser
from ultis.socket_helper import send_to_socket, get_socket_data_livestream


@shared_task
def send_message_to_user(user_id, live_id, data, event):
    send_to_socket(app='discovery',
                   name=str(user_id),
                   data=get_socket_data_livestream(event=event, data=data, live_id=live_id))


@shared_task
def send_new_message_to_live(live_id, msg_id):
    all_users = LiveUser.objects.select_related('live_streaming').filter(live_streaming__id=live_id)
    message = MessageLive.objects.get(id=msg_id)
    data = MessageLiveSerializer(message).data
    # Create a group of tasks to send messages to all users concurrently
    tasks = group(
        send_message_to_user.s(str(live_user.user.id), live_id, data, event='NEW_MESSAGE') for live_user in all_users)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def send_new_update_live(live_id, data):
    all_users = LiveUser.objects.select_related('live_streaming').filter(live_streaming__id=live_id)
    tasks = group(
        send_message_to_user.s(str(live_user.user.id), live_id, data, event='NEW_LIVE_UPDATE') for live_user in
        all_users)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def send_emoji_to_live(emoji_log_id):
    emoji_log = EmojiLog.objects.select_related('live').get(id=emoji_log_id)
    data = EmojiLogSerializer(emoji_log).data
    all_live_users = LiveUser.objects.select_related('live_streaming', 'user').filter(
        live_streaming_id=emoji_log.live.id)
    # for live_user in all_live_users:
    #     send_to_socket(app='discovery',
    #                    name=str(live_user.user.id),
    #                    data=get_socket_data_livestream(event='NEW_EMOJI', data=data, live_id=str(emoji_log.live.id)))
    tasks = group(
        send_message_to_user.s(str(live_user.user.id), str(emoji_log.live.id), data, event='NEW_EMOJI') for live_user in
        all_live_users)

    # Execute the group of tasks
    tasks.apply_async()

    emoji_log.delete()


@shared_task
def send_gift_to_live(gift_log_id):
    gift_log = GiftLog.objects.get(id=gift_log_id)
    data = GiftLogSerializer(gift_log).data

    all_live_users = LiveUser.objects.select_related('live_streaming', 'user').filter(
        live_streaming_id=gift_log.live_streaming.id)

    # for live_user in all_live_users:
    #     send_to_socket(app='discovery',
    #                    name=str(live_user.user.id),
    #                    data=get_socket_data_livestream(event='NEW_GIFT', data=data,
    #                                                    live_id=str(gift_log.live_streaming.id)))
    tasks = group(
        send_message_to_user.s(str(live_user.user.id), str(gift_log.live_streaming.id), data, event='NEW_GIFT') for
        live_user in all_live_users)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def send_new_join_leave_to_live(live_id, live_user_id, event):
    all_users = LiveUser.objects.select_related('live_streaming').filter(live_streaming__id=live_id)
    new_user = LiveUser.objects.get(id=live_user_id)
    data = LiveUserSerializer(new_user).data

    tasks = group(
        send_message_to_user.s(str(live_user.user.id), live_id, data, event=event) for live_user in all_users)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def send_new_live_to_user(live_id, data):
    all_users_online = CustomUser.objects.filter(is_fake=False, is_online=True)
    # for user in all_users_online:
    #     send_to_socket(app='discovery',
    #                    name=str(user.id),
    #                    data=get_socket_data_livestream(event='NEW_LIVE_CREATE', data=data, live_id=live_id))
    tasks = group(
        send_message_to_user.s(str(user.id), live_id, data, event='NEW_LIVE_CREATE') for user in all_users_online)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def send_action_from_host_to_user_in_live(live_id, live_user_id, event):
    all_users = LiveUser.objects.select_related('live_streaming').filter(live_streaming__id=live_id)

    live_user = LiveUser.objects.get(id=live_user_id)
    data = LiveUserSerializer(live_user).data

    # for live_user in all_users:
    #     send_to_socket(app='discovery',
    #                    name=str(live_user.user.id),
    #                    data=get_socket_data_livestream(event=event, data=data, live_id=live_id))
    tasks = group(
        send_message_to_user.s(str(live_user.user.id), live_id, data, event=event) for live_user in all_users)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def send_action_from_user_to_live(live_id, live_user_id, event):
    all_users = LiveUser.objects.select_related('live_streaming').filter(live_streaming__id=live_id)

    live_user = LiveUser.objects.get(id=live_user_id)
    data = LiveUserSerializer(live_user).data

    # for live_user in all_users:
    #     send_to_socket(app='discovery',
    #                    name=str(live_user.user.id),
    #                    data=get_socket_data_livestream(event=event, data=data, live_id=live_id))
    tasks = group(
        send_message_to_user.s(str(live_user.user.id), live_id, data, event=event) for live_user in all_users)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def send_from_host_to_user_in_live(live_id, event):
    # all_users = LiveUser.objects.select_related('live_streaming').filter(live_streaming__id=live_id)
    all_users = CustomUser.objects.filter(is_fake=False, is_online=True)
    tasks = group(
        send_message_to_user.s(str(user.id), live_id, {}, event=event) for user in all_users)

    # Execute the group of tasks
    tasks.apply_async()


@shared_task
def disconnect_live(user_id):
    list_live_user = LiveUser.objects.filter(user__id=user_id,
                                             ).exclude(live_streaming__type='STREAM')
    try:
        for live_user in list_live_user:
            live_user.leave_room()
            live_user.live_streaming.less_view(live_user)
            if live_user.is_live:
                live_user.set_live(False)
                send_new_join_leave_to_live.s(live_id=str(live_user.live_streaming.id),
                                              live_user_id=str(live_user.id),
                                              event='NEW_LEAVE_CHAIR').apply_async(countdown=0)

            send_new_join_leave_to_live.s(live_id=str(live_user.live_streaming.id),
                                          live_user_id=str(live_user.id),
                                          event='NEW_LEAVE').apply_async(countdown=0)
    except Exception as e:
        logging(e)
