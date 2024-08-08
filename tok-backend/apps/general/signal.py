from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from minio import Minio

from api.services.firebase import send_and_save_notification
from apps.discovery.models import LiveStreamingHistory
from apps.general.models import Report, FileUpload
from apps.user.models import ReportMessage
from core.settings import AWS_S3_ENDPOINT_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
from ultis.socket_friend_helper import send_noti_report_to_user
from ultis.socket_helper import send_to_socket, get_socket_data


@transaction.atomic
@receiver(post_save, sender=Report)
def report_saved(sender, instance, created, **kwargs):
    if instance.is_verified:
        if instance.type == 'MESSAGE':
            rp = ReportMessage.objects.get_or_create(user=instance.direct_user)[0]
            msg = rp.new_verified_report()
            send_and_save_notification(user=instance.direct_user,
                                       body=msg)
        elif instance.type == 'BLOG':
            ...
            msg = ''
        else:
            live = LiveStreamingHistory.objects.get(id=instance.fk_id)
            live.delete()
            if instance.note == '':
                reason = 'Vi phạm tiêu chuẩn cộng đồng'
            else:
                reason = instance.note
            msg = f'Phiên live của bạn đã bị xoá với lí do: {reason}'
            send_to_socket('discovery', str(instance.fk_id), get_socket_data('NEW_BAN', None))

            send_and_save_notification(user=instance.direct_user,
                                       title='Cảnh cáo vi phạm',
                                       body=msg,
                                       direct_type='',
                                       direct_value='',
                                       direct_user=None,
                                       type_noti='SYSTEM'
                                       )


@receiver(pre_delete, sender=FileUpload)
def delete_file_from_minio(sender, instance, **kwargs):
    """
    Xóa file từ Minio khi một đối tượng FileUpload bị xóa.
    """
    if instance.file_url:
        try:
            minioClient = Minio(endpoint=AWS_S3_ENDPOINT_URL.replace('https://', ''),
                                access_key=AWS_ACCESS_KEY_ID,
                                secret_key=AWS_SECRET_ACCESS_KEY,
                                secure=False)
            minioClient.remove_object(AWS_STORAGE_BUCKET_NAME, instance.file_url)
        except Exception as e:
            print(f"Failed to delete file from Minio: {e}")
