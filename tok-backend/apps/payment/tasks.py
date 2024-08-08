from celery import shared_task
from django.utils import timezone

from api.services.firebase import send_and_save_notification
from apps.payment.models import Transaction
from apps.user.models import CustomUser, UserVip


@shared_task
def check_timeout_payment(transaction_id):
    transaction = Transaction.objects.get(id=transaction_id)
    if transaction.return_code == '02':
        transaction.update_deposit_status('01')


@shared_task
def send_vip_expiration_reminder(user_id):
    user_vip = UserVip.objects.get(user__id=user_id)
    now = timezone.now()
    date_expired = user_vip.date_end - now
    if date_expired.days <= 3:
        send_and_save_notification(user=user_vip.user,
                                   title='Thông báo',
                                   body='Gói vip sắp hết hạn, hãy gia hạn để không bị bỏ lỡ các tính năng của VIP')


@shared_task
def reset_vip_settings(user_id):
    user_vip = UserVip.objects.get(user__id=user_id)
    now = timezone.now()

    if user_vip.date_end <= now:
        user = user_vip.user
        user.setting_vip = {
            'hide_age': False,
            'hide_gender': False,
            'hide_location': False,
            'prevent_search': False,
            'hide_avt_frame': False,
        }
        user.save()
        send_and_save_notification(user=user_vip.user,
                                   title='Thông báo',
                                   body='Gói đã hết hạn, hãy gia hạn để không bị bỏ lỡ các tính năng của VIP')


@shared_task
def check_and_send_vip_expiration_reminders():
    now = timezone.now() - timezone.timedelta(hours=24)
    user_vips = UserVip.objects.filter(date_end__lt=now)

    for user_vip in user_vips:
        send_vip_expiration_reminder(user_vip.user.id)


@shared_task
def check_and_reset_vip_settings():
    now = timezone.now()
    user_vips = UserVip.objects.filter(date_end__lte=now)

    for user_vip in user_vips:
        reset_vip_settings(user_vip.user.id)
