import datetime

from django.utils import timezone
from rest_framework import serializers

from api.services.agora.main import get_token_publisher
from apps.general.models import DefaultAvatar
from apps.discovery.models import LiveStreamingHistory, Gift, MessageLive, GiftLog, Emoji, EmojiLog, LiveUser, UserGift
from apps.general.serializers import FileUploadSerializer, StickerSerializer
from apps.user.models import CustomUser, UserVip


class UserLiveViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'full_name',
                  'avatar']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = str(instance.id)
        data['avatar'] = instance.get_avatar
        data['avatar_frame'] = instance.get_avatar_frame
        vip = UserVip.objects.get_or_create(user=instance)[0]
        data['is_vip'] = False
        if vip.date_start is not None and vip.date_end :
            if vip.date_end > timezone.now():
                data['is_vip'] = True
        data = instance.check_vip(data)
        return data


class LiveStreamingSerializer(serializers.ModelSerializer):
    host = UserLiveViewSerializer()

    class Meta:
        model = LiveStreamingHistory
        exclude = ['view', 'gift', 'comment', 'coin', 'diamond', 'duration', 'created_at', 'updated_at',
                   'is_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.cover_image:
            data['cover_image'] = str(instance.cover_image.file.url)
        data['room_token'] = instance.room_token
        # if instance.host:
        #     data['agora_token'] = get_token_publisher(str(instance.id), str(instance.host.id))

        return data


class ListLiveSerializer(serializers.ModelSerializer):
    host = UserLiveViewSerializer()

    class Meta:
        model = LiveStreamingHistory
        exclude = ['view', 'gift', 'comment', 'coin', 'diamond', 'duration', 'created_at', 'updated_at',
                   'is_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.cover_image:
            data['cover_image'] = str(instance.cover_image.file.url)
        data['room_token'] = instance.room_token
        # if instance.host:
        #     data['agora_token'] = get_token_publisher(str(instance.id), str(instance.host.id) or '')

        return data


class LiveUserSerializer(serializers.ModelSerializer):
    user = UserLiveViewSerializer()

    class Meta:
        model = LiveUser
        fields = ['user', 'role', 'is_live', 'is_on_mic']


class GiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gift
        fields = ['id',
                  'title',
                  'image',
                  'price']


class EmojiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emoji
        fields = ['id',
                  'image', ]


class EmojiLogSerializer(serializers.ModelSerializer):
    sender = UserLiveViewSerializer()
    emoji = EmojiSerializer()

    class Meta:
        model = EmojiLog
        exclude = ['updated_at', 'live']


class GiftLogSerializer(serializers.ModelSerializer):
    gift = GiftSerializer()
    receiver = UserLiveViewSerializer(many=True)
    sender = UserLiveViewSerializer()

    class Meta:
        model = GiftLog
        exclude = ['live_streaming', 'updated_at']


class MessageLiveSerializer(serializers.ModelSerializer):
    sender = UserLiveViewSerializer()
    file = FileUploadSerializer(many=True)
    sticker = StickerSerializer()

    class Meta:
        model = MessageLive
        exclude = ['gift_log']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['live'] = str(instance.live.id)
        return data


class LiveUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStreamingHistory
        fields = ['cover_image', 'name', 'description']


class UserGiftSerializer(serializers.ModelSerializer):
    gift = GiftSerializer()

    class Meta:
        model = UserGift
        fields = ['gift']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['gift']['total_quantity'] = instance.quantity
        return data['gift']
