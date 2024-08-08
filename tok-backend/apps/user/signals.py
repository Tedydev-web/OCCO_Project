from itertools import chain

from celery import shared_task
from django.core.cache import cache
from django.db.models import Q, Subquery
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.general.models import DevSetting
from apps.user.models import FriendShip, CustomUser
from apps.user.serializers import BaseInforUserSerializer
from ultis.socket_helper import get_socket_data, send_noti_to_socket_user


@receiver(post_save, sender=CustomUser)
def send_notification_user_contact(sender, instance, **kwargs):
    # Set cache
    cache_key = f"user_info_{instance.id}"
    cache.delete(cache_key)
    cache.set(cache_key, BaseInforUserSerializer(instance).data, timeout=int(DevSetting.get_value('cache_time_out')))

