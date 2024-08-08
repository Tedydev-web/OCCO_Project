from rest_framework import serializers

from .models import Notification, UserDevice
from ..general.models import DefaultAvatar
from ..user.serializers import UserFriendShipSerializer
from django.utils.translation import gettext_lazy as _


class NotificationSerializer(serializers.ModelSerializer):
    direct_user = UserFriendShipSerializer()

    class Meta:
        model = Notification
        fields = ['id',
                  'direct_user',
                  'type',
                  'title',
                  'body',
                  'is_read',
                  'custom_data',
                  'direct_type',
                  'direct_value',
                  'created_at',
                  'user']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if not instance.direct_user:
            data['direct_user'] = {
                'id': None,
                'full_name': "Hệ thống",
                "avatar": str(DefaultAvatar.objects.get(key='avatar').image.url),
            }
        data['body'] = instance.body_vi if instance.body_vi else instance.body_en
        data['user'] = str(instance.user.id)
        return data


class UserDeviceSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = UserDevice
        fields = '__all__'
