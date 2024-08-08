from api.services.firebase import send_and_save_notification, send_not_save_notification
from apps.notification.serializers import NotificationSerializer
from ultis.socket_helper import get_socket_data, send_noti_to_socket_user, send_to_socket, get_socket_data_conversation


def send_noti_add_friend(sender, receiver):
    body = 'Đã gửi lời mời kết bạn'
    direct_user = sender
    type_noti = 'FRIEND'
    custom_data = {'type': 'request_friend'}
    send_not_save_notification(user=receiver,
                               title=sender.full_name,
                               body=body,
                               custom_data=custom_data)

    send_noti_to_socket_user(str(receiver.id), get_socket_data('NEW_FRIEND_REQUEST', str(direct_user.id)))


def send_noti_accept_friend(sender, receiver):
    body = f'Đã đồng ý lời mời kết bạn'
    direct_user = receiver
    type_noti = 'FRIEND'
    custom_data = {'type': 'accept_friend'}

    send_not_save_notification(user=sender,
                               title=receiver.full_name,
                               body=body,
                               custom_data=custom_data)

    send_noti_to_socket_user(str(sender.id), get_socket_data('NEW_FRIEND_ACCEPT', str(receiver.id)))


def send_noti_report_to_user(sender, count):
    title = 'Cảnh báo vi phạm vi định'
    body = f'Bạn đã bị ghi nhận vi phạm vi định {count} lần'
    type_noti = 'SYSTEM'

    notification = send_and_save_notification(user=sender,
                                              title=title,
                                              body=body,
                                              type_noti=type_noti)
    data_serializer = NotificationSerializer(notification).data

    send_noti_to_socket_user(str(sender.id), get_socket_data('NEW_NOTIFICATION', data_serializer))
