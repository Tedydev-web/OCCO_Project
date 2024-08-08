import datetime

import pytz
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.conversation.models import Room, Message, Call, RoomUser, PinnedMessage, SeenByMessage
from apps.discovery.serializers import GiftLogSerializer

from apps.general.models import DefaultAvatar, Report, FileUpload, BackGroundColor

from apps.general.models import DefaultAvatar
from apps.general.serializers import FileUploadSerializer, StickerSerializer

from apps.user.models import CustomUser, UserVip
from ultis.validate import banned_words


class BackGroundColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackGroundColor
        fields = ['id', 'color', 'title']


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'full_name',
                  'avatar',
                  'is_online',
                  'is_private',
                  'setting_private']

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


class RoomUserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomUser
        fields = ['user', 'role', 'last_active']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['user'] = UserBasicSerializer(instance.user).data

        return data


class CallSerializer(serializers.ModelSerializer):
    call_name = serializers.SerializerMethodField()

    class Meta:
        model = Call
        fields = "__all__"

    def get_call_name(self, instance):
        if instance.status in ['WAITING', 'ACCEPTED', 'HANGUP']:
            return 'Cuộc gọi thoại' if instance.type == "CALL" else "Cuộc gọi video"
        else:
            return 'Cuộc gọi thất bại'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('id')
        timezone = pytz.timezone('Asia/Bangkok')  # Thay 'Asia/Bangkok' bằng múi giờ mong muốn của bạn

        if instance.start_time and instance.end_time:
            # Chuyển đổi các đối tượng datetime sang múi giờ +07:00
            start_time = instance.start_time.astimezone(timezone).replace(tzinfo=None)
            end_time = instance.end_time.astimezone(timezone).replace(tzinfo=None)

            # Tính toán khoảng thời gian giữa end_time và start_time
            duration_seconds = (end_time - start_time).total_seconds()

            # Trả về kết quả
            data['last'] = int(duration_seconds)
        else:
            data['last'] = None
        data.pop('updated_at')
        return data


class MessageReplySerializer(serializers.ModelSerializer):
    sticker = StickerSerializer()
    gift = GiftLogSerializer()

    class Meta:
        model = Message
        exclude = ['deleted_by', 'reply_to', 'forwarded_from']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['room'] = str(instance.room.id)
        data['sender'] = UserBasicSerializer(instance.sender).data

        if instance.file:
            data['file'] = FileUploadSerializer(instance.file, many=True).data

        try:
            request = self.context.get('request')
            if instance.call:
                data['call'] = CallSerializer(instance.call, context={'request': request}).data
        except Exception as e:
            data['call'] = None
        data['created_at'] = data['created_at'].split('+')[0] if '+' in data['created_at'] else data['created_at']

        return data


class SeenBySerializer(serializers.ModelSerializer):
    user = UserBasicSerializer()

    class Meta:
        model = SeenByMessage
        fields = ['user', 'date_seen']


class MessageSerializer(serializers.ModelSerializer):
    # file = FileUploadSerializer(many=True)
    reply_to = MessageReplySerializer()
    forwarded_from = MessageReplySerializer()
    sticker = StickerSerializer()
    gift = GiftLogSerializer()

    class Meta:
        model = Message
        exclude = ['deleted_by', ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['room'] = str(instance.room.id)
        data['sender'] = UserBasicSerializer(instance.sender).data

        if instance.file:
            data['file'] = FileUploadSerializer(instance.file, many=True).data

        try:
            request = self.context.get('request')
            if instance.call:
                data['call'] = CallSerializer(instance.call, context={'request': request}).data
        except Exception as e:
            data['call'] = None
        data['created_at'] = data['created_at'].split('+')[0] if '+' in data['created_at'] else data['created_at']
        data['seen_by'] = SeenBySerializer(instance.seenbymessage_set.all().select_related('message', 'user'),
                                           many=True).data
        return data


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = self.context.get('request').user

        # Access prefetched related objects directly
        room_users = instance.roomuser_set.select_related('user', 'user__avatar').all()

        other = next((ru for ru in room_users if ru.user != user), None)

        type_info = {
            'RANDOM': {'name': 'Ngẫu nhiên', 'image': f'{DefaultAvatar.objects.get(key="random").image.url}'},
            'PRIVATE': {'name': f'Ẩn danh - {str(instance.id)[-6:].upper()}',
                        'image': f'{DefaultAvatar.objects.get(key="anonymous").image.url}'},
            'CONNECT': {'name': f'{other.user.full_name}', 'image': f'{other.user.get_avatar}'} if other else {
                'name': '', 'image': ''},
            'GROUP': {'name': f'{instance.name}', 'image': f'{instance.get_image}'},
            'CSKH': {'name': f'{other.user.full_name}', 'image': f'{other.user.get_avatar}'} if other else {
                'name': '', 'image': ''},
        }
        info = type_info.get(instance.type)
        data['name'] = info.get('name')
        data['image'] = info.get('image')

        rs = next((ru for ru in room_users if ru.user == user), None)

        data['total_unseen'] = rs.total_unseen
        data['last_message'] = rs.last_message

        if other:
            data['block_status'] = CustomUser.custom_objects.is_block(user, other.user)

        data['list_users'] = RoomUserBasicSerializer(room_users, many=True).data
        data['created_at'] = data['created_at'].split('+')[0] if '+' in data['created_at'] else data['created_at']
        data['background_color'] = None
        if instance.background_color:
            data['background_color'] = str(
                instance.background_color.color) if instance.background_color.is_active else None
        data['background_image'] = str(instance.background_image.file.url) if instance.background_image else None
        return data


class ListRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        exclude = ['is_accepted', 'is_leaved', 'updated_at', 'is_used']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = self.context.get('request').user

        # Access prefetched related objects directly
        try:
            room_users = instance.room_users
        except:
            room_users = list(instance.roomuser_set.select_related('user', 'user__avatar').all())

        other = next((ru for ru in room_users if ru.user != user), None)

        type_info = {
            'RANDOM': {'name': 'Ngẫu nhiên', 'image': f'{DefaultAvatar.objects.get(key="random").image.url}'},
            'PRIVATE': {'name': f'Ẩn danh - {str(instance.id)[-6:].upper()}',
                        'image': f'{DefaultAvatar.objects.get(key="anonymous").image.url}'},
            'CONNECT': {'name': f'{other.user.full_name}', 'image': f'{other.user.get_avatar}'} if other else {
                'name': '', 'image': ''},
            'GROUP': {'name': f'{instance.name}', 'image': f'{instance.get_image}'},
            'CSKH': {'name': f'{other.user.full_name}', 'image': f'{other.user.get_avatar}'} if other else {
                'name': '', 'image': ''},
        }
        info = type_info.get(instance.type)
        data['name'] = info.get('name')
        data['image'] = info.get('image')

        rs = next((ru for ru in room_users if ru.user == user), None)
        if instance.type == 'PRIVATE':
            data['block_status'] = rs.block_status_private
        else:
            if other:
                data['block_status'] = CustomUser.custom_objects.is_block(user, other.user)

        data['notification_mode'] = rs.notification_mode
        data['last_message'] = rs.last_message
        data['total_unseen'] = rs.total_unseen
        data['list_users'] = RoomUserBasicSerializer(room_users, many=True).data
        data['created_at'] = data['created_at'].split('+')[0] if '+' in data['created_at'] else data['created_at']
        data['is_pinned_msg'] = PinnedMessage.objects.select_related('room').filter(room=instance).exists()
        data['background_color'] = None
        if instance.background_color:
            data['background_color'] = str(
                instance.background_color.color) if instance.background_color.is_active else None
        data['background_image'] = str(instance.background_image.file.url) if instance.background_image else None
        return data


class LastMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'text', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.type == 'CALL':
            data['text'] = 'Cuộc gọi thoại'
        if 'VIDEO' in instance.type:
            data['text'] = 'Cuộc gọi video'

        data['created_at'] = data['created_at'].split('+')[0] if '+' in data['created_at'] else data['created_at']
        return data


class RoomDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['image'] = instance.image.file_url
            data['list_users'] = RoomUserBasicSerializer(
                instance.roomuser_set.roomuser_set.select_related('user', 'user__avatar').all(), many=True).data
        except Exception as e:
            print(e)
        data['created_at'] = data['created_at'].split('+')[0] if '+' in data['created_at'] else data['created_at']
        data['newest_at'] = data['newest_at'].split('+')[0] if '+' in data['newest_at'] else data['newest_at']

        return data


class RoomSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id',
                  'name']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        try:
            data['image'] = instance.image.file_url
            data['list_users'] = RoomUserBasicSerializer(
                instance.roomuser_set.select_related('user', 'user__avatar').all(), many=True).data
        except Exception as e:
            print(e)
        return data


class MessageCreateSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)
    type = serializers.ChoiceField(choices=Message.TYPE_CHOICES, required=True)
    text = serializers.CharField(required=False, allow_blank=True)
    file = serializers.PrimaryKeyRelatedField(queryset=FileUpload.objects.all(), many=True, required=False)

    class Meta:
        model = Message
        fields = ['id', 'type', 'text', 'file', 'reply_to', 'forwarded_from', 'sticker', "style_text"]

    def validate(self, data):
        text = data.get('text', '')
        words = text.split()  # Tách từ dựa trên khoảng trắng
        for word in words:
            if word.lower() in banned_words:
                raise ValidationError('Tồn tại nội dung vi phạm qui tắc cộng đồng.', code='invalid')
        return data

    def create(self, validated_data):
        files = validated_data.pop('file', [])
        validated_data['sender'] = self.context['request'].user
        validated_data['room'] = self.context['room']

        msg_id = validated_data.pop('id', None)
        if msg_id:
            msg = Message(id=msg_id, **validated_data)
        else:
            msg = Message(**validated_data)

        msg.full_clean()  # Kiểm tra và chạy các validators
        msg.save()
        if msg.room.type == 'PRIVATE':
            sender_name = "Người dùng ẩn danh"
        else:
            sender_name = msg.sender.full_name
        if files:
            msg.file.set(files)
            msg.text = f"{sender_name} đã chia sẻ {len(files)} file"

        if 'CALL' in msg.type:
            call = Call.objects.create(type=msg.type,
                                       status='WAITING')
            msg.call = call
        if msg.type == 'AUDIO':
            msg.text = f"{sender_name} đã gửi một tin nhắn thoại"
        if msg.type == 'STICKER':
            msg.text = f"{sender_name} đã gửi một nhãn dán"
        if msg.type == 'LOCATION':
            msg.add_location_message(lat=self.context.get('request').data['lat'],
                                     lng=self.context.get('request').data['lng'],
                                     text=self.context.get('request').data['location_text'])
            msg.text = f"{sender_name} đã chia sẻ vị trí"
        msg.save()
        return msg


class PinnedMessageSerializer(serializers.ModelSerializer):
    message = MessageSerializer()
    pinner = UserBasicSerializer()

    class Meta:
        model = PinnedMessage
        fields = ['id', 'pinner', 'message', 'created_at']


class MessageIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data = data['id']
        return data
