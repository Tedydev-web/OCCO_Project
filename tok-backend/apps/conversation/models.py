import datetime
import uuid
from collections import deque

from django.db import models
from django.db.models import Prefetch
from rest_framework.exceptions import ValidationError

from apps.discovery.models import Gift, GiftLog
from apps.general.models import FileUpload, DefaultAvatar, DevSetting, BackGroundColor, Sticker
from apps.user.models import CustomUser
from ultis.validate import JsonWordValidator, banned_words


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ROOM_TYPE_CHOICES = (
        ('RANDOM', 'Ngẫu nhiên'),
        ('PRIVATE', 'Ẩn danh'),
        ('CONNECT', 'Thông thường'),
        ('GROUP', 'Nhóm'),
        ('CSKH', 'Chăm sóc khách hàng')
    )
    type = models.CharField(max_length=12, choices=ROOM_TYPE_CHOICES, null=True, blank=True, verbose_name='Loại phòng')

    image = models.ForeignKey(FileUpload, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ảnh")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên phòng",
                            validators=[JsonWordValidator(banned_words)])

    # For random and private room
    is_used = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_leaved = models.BooleanField(default=False)

    newest_at = models.DateTimeField(null=True, blank=True, db_index=True, verbose_name='Tin nhắn cuối vào')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True)

    # Background
    background_image = models.ForeignKey(FileUpload, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='background')
    background_color = models.ForeignKey(BackGroundColor, on_delete=models.SET_NULL, null=True, blank=True)

    # block_2_user = models.CharField(choices=(
    #     ('BLOCK', 'Chặn'),
    #     ('BLOCKED', 'Bị chặn'),
    # ), null=True, blank=True)

    def set_used(self):
        self.is_used = True
        self.save()

    def set_leaved(self):
        self.is_leaved = True
        self.save()

    def set_connect(self):
        self.type = 'CONNECT'
        self.save()

    def set_newest(self):
        self.newest_at = datetime.datetime.now()
        self.save()

    @property
    def get_image(self):
        if self.image is None:
            return str(DefaultAvatar.objects.first().image.url)

        return str(self.image.file.url)

    class Meta:
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'


class RoomUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ROLE_CHOICES = (
        ('HOST', 'Chủ nhóm'),
        ('KEY', 'Phó nhóm'),
        ('USER', 'Thành viên')
    )
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, null=True, blank=True, verbose_name="Chức danh")

    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Phòng")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Thành viên")

    date_removed = models.DateTimeField(null=True, blank=True)
    is_removed = models.BooleanField(default=False)

    last_active = models.DateTimeField(auto_now_add=True)

    last_message = models.JSONField(default=dict, null=True)
    total_unseen = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True)

    # Notification
    notification_mode = models.CharField(choices=(
        ('on', 'Bật'),
        ('off', 'Tắt'),
    ), default='on')

    # Block private
    block_status_private = models.CharField(choices=(
        ('BLOCK', 'Chặn'),
        ('BLOCKED', 'Bị chặn'),
    ), null=True, blank=True)

    def set_active(self):
        self.last_active = datetime.datetime.now()
        self.save()

    def set_new_role(self, role):
        self.role = role
        self.save()

    def set_last_message(self, msg):
        self.last_message = msg
        self.save()

    def set_total_unseen(self):
        self.total_unseen += 1
        self.save()

    def reset_total_unseen(self):
        self.total_unseen = 0
        self.save()

    class Meta:
        verbose_name = 'Thành viên'
        verbose_name_plural = 'Thành viên'


class Call(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    CALL_TYPE = (
        ('CALL', 'Cuộc gọi thoại'),
        ('VIDEO_CALL', 'Cuộc gọi video')
    )
    CALL_STATUS = (
        ('WAITING', 'Chờ chấp nhận'),
        ('ACCEPTED', 'Chấp nhận'),
        ('CANCELED', 'Đã huỷ'),
        ('REJECTED', 'Từ chối'),
        ('MISSED', 'Bị nhỡ'),
        ('HANGUP', 'Kết thúc')
    )
    status = models.CharField(max_length=10, default="waiting", verbose_name="Trạng thái")
    type = models.CharField(choices=CALL_TYPE, max_length=10, default='call', verbose_name="Loại")

    last = models.CharField(max_length=255, verbose_name="Thời gian cuộc gọi", default="")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian bắt đầu")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Thời gian kết thúc")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True)

    def set_type(self, type_call):
        self.type = type_call
        self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    def start_call(self):
        self.start_time = datetime.datetime.now()
        self.save()

    def end_call(self):
        self.end_time = datetime.datetime.now()
        # self.last = str(self.end_time-self.start_time)
        self.save()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người gửi')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Phòng')
    call = models.OneToOneField(Call, on_delete=models.DO_NOTHING, null=True, blank=True)

    TYPE_CHOICES = (
        ('TEXT', 'Văn bản'),
        ('AUDIO', 'Âm thanh'),
        ('VIDEO', 'Video'),
        ('IMAGE', 'Hình ảnh'),
        ('FILE', 'File'),
        ('GIFT', 'Quà tặng'),
        ('CALL', 'Gọi'),
        ('VIDEO_CALL', 'Gọi'),
        ('HISTORY', 'Lịch sử'),
        ('LOCATION', 'Vị trí'),
        ('STICKER', 'Nhãn dán')
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, null=True, blank=True, verbose_name='Loại')

    text = models.TextField(null=True, blank=True, validators=[JsonWordValidator(banned_words)])
    file = models.ManyToManyField(FileUpload)

    deleted_by = models.ManyToManyField(CustomUser, default=list, related_name="deleted_by")
    is_revoked = models.BooleanField(default=False)
    is_seen = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Gửi vào')
    update_at = models.DateTimeField(auto_now=True)

    # Reply message
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies',
                                 verbose_name='Trả lời tin nhắn')

    # Forward from
    forwarded_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='forwarded_messages', verbose_name='Chuyển tiếp từ tin nhắn')

    # Location share
    location = models.JSONField(null=True, blank=True)

    # Sticker
    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE, null=True, blank=True)

    # Style text
    style_text = models.TextField(null=True, blank=True)

    # Gift
    gift = models.ForeignKey(GiftLog, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.text or ''

    def add_location_message(self, lat, lng, text):
        self.location = {'lat': lat, 'lng': lng, 'text': text}
        self.save()

    class Meta:
        verbose_name = 'Tin nhắn'
        verbose_name_plural = 'Tin nhắn'


class SeenByMessage(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_seen = models.DateTimeField(auto_now_add=True)


class PinnedMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pinner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class RandomQueue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_RANDOM = (
        ('CHAT', 'Nhắn tin'),
        ('CALL', 'Gọi'),
    )

    is_stop = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TYPE_RANDOM, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.full_name


class PrivateQueue(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_RANDOM = (
        ('CHAT', 'Nhắn tin'),
        ('CALL', 'Gọi'),
    )

    is_stop = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TYPE_RANDOM, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
