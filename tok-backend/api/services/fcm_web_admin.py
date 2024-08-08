from pyfcm import FCMNotification

from apps.dashboard.models import FCMToken


def send_push_notification(registration_ids, message_title, message_body):
    push_service = FCMNotification("serviceAccountTOK.json",
                                   "toktok-7c498"
                                   )
    params_list = [
        {
            'registration_id': reg_id,
            'message_title': message_title,
            'message_body': message_body,
        }
        for reg_id in registration_ids
    ]

    # Gửi thông báo đến nhiều thiết bị
    result = push_service.async_notify_multiple_devices(params_list=params_list)
    return result


# Gọi hàm này để gửi thông báo
registration_ids = FCMToken.objects.all().values_list('token', flat=True)
send_push_notification(registration_ids, "Title", "Message")
