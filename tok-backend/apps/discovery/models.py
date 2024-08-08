import io
import uuid
from itertools import chain

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

from api.services.agora.main import get_token_publisher, get_token_subscriber
from api.services.stringee import get_room_token
from apps.general.models import FileUpload, Sticker
from apps.user.models import CustomUser
from ultis.validate import JsonWordValidator, banned_words


# Create your models here.
class LiveStreamingHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_show = models.CharField(unique=True, max_length=20, null=True, blank=True, verbose_name='ID Hiển thị')

    TYPE_CHOICES = (
        ('CHAT', 'Chat'),
        ('AUDIO', 'Audio'),
        ('VIDEO', 'Video'),
        ('STREAM', 'Stream'),
    )
    type = models.CharField(choices=TYPE_CHOICES, max_length=6, null=True, blank=True, verbose_name='Loại phòng')
    name = models.CharField(max_length=255, null=True, blank=True, validators=[JsonWordValidator(banned_words)],
                            verbose_name='Tên phòng')
    title = models.CharField(max_length=255, default='')

    host = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Chủ phòng')
    COUNTRY_CHOICES = (
        ('VI', 'Việt Nam'),
        ('--', '--')
    )
    country = models.CharField(max_length=255, choices=COUNTRY_CHOICES, null=True, blank=True, verbose_name='Quốc gia')

    SIDE_CHOICES = (
        ('NORTH', 'Miền bắc'),
        ('CENTRAL', 'Miền trung'),
        ('SOUTH', 'Miền nam'),
        ('ALL', 'Toàn quốc')
    )
    side = models.CharField(max_length=255, choices=SIDE_CHOICES, null=True, blank=True, verbose_name='Miền')

    province = models.CharField(max_length=255, null=True, blank=True, verbose_name='Tỉnh thành')

    user_view = models.IntegerField(default=0, verbose_name='Lượt xem')
    view = models.JSONField(null=True, blank=True, default=dict)

    description = models.CharField(max_length=255, null=True, blank=True, validators=[JsonWordValidator(banned_words)],
                                   verbose_name='Mô tả')
    max_chairs = models.IntegerField(default=12)

    gift = models.IntegerField(default=0)
    comment = models.IntegerField(default=0)
    coin = models.IntegerField(default=0)
    diamond = models.IntegerField(default=0)

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(auto_now=True)
    duration = models.IntegerField(default=0)

    cover_image = models.ForeignKey(FileUpload, on_delete=models.CASCADE, null=True)

    agora_token = models.TextField(default='')
    agora_user_token = models.TextField(default='')

    is_stopped = models.BooleanField(default=False)
    is_hide = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True)

    def add_view(self, live_user):
        if self.view is None:
            self.view = {}
        user = live_user.user
        user_id = str(user.id)
        if user_id not in self.view:
            self.view[user_id] = {
                'id': user_id,
                'full_name': user.full_name,
                'avatar': user.get_avatar,
                'role': live_user.role,
                'is_live': live_user.is_live
            }
            self.user_view = len(self.view)
        self.save()

    def less_view(self, live_user):
        if self.view is not None:
            user = live_user.user
            user_id = str(user.id)
            if user_id in self.view:
                del self.view[user_id]
                self.user_view = len(self.view)

        if self.user_view <= 0 and self.type == 'STREAM':
            self.user_view = 0
            self.is_stopped = True

        self.save()

    @property
    def room_token(self):
        return get_room_token(str(self.id))

    def save(self, *args, **kwargs):
        if self.id_show is None:
            self.id_show = str(self.id)[-8:].upper()

        if self.host is not None:
            self.agora_token = get_token_publisher(str(self.id), str(self.host.id))
            self.agora_user_token = get_token_subscriber(str(self.id), str(self.host.id))
        super(LiveStreamingHistory, self).save(*args, **kwargs)


class LiveUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ROLE_CHOICES = (
        ('HOST', 'Chủ nhóm'),
        ('KEY', 'Phó nhóm'),
        ('USER', 'Thành viên')
    )
    role = models.CharField(max_length=4, choices=ROLE_CHOICES, null=True, blank=True, verbose_name="Chức danh")

    coin = models.IntegerField(default=0)
    diamond = models.IntegerField(default=0)

    agora_token = models.TextField(default='')

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Người xem')
    live_streaming = models.ForeignKey(LiveStreamingHistory, on_delete=models.CASCADE)

    is_on_mic = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    last_join = models.DateTimeField(auto_now=True, verbose_name='Tham gia vào')

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def set_role(self, role):
        self.role = role
        self.save()

    def leave_room(self):
        self.is_online = False
        self.save()

    def join_room(self):
        self.is_online = True
        self.save()

    def set_live(self, is_live):
        self.is_live = is_live
        self.save()

    def set_micro(self, is_on):
        self.is_on_mic = is_on
        self.save()

    class Meta:
        verbose_name = 'Người xem'
        verbose_name_plural = 'Người xem'


class Gift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=15, verbose_name='Tên')
    image = models.ImageField(upload_to='assets/image/gift', verbose_name='Ảnh quà tặng')

    price = models.PositiveIntegerField(default=0, verbose_name='Giá')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quà tặng'
        verbose_name_plural = 'Quà tặng'

    def __str__(self):
        return self.title_vi

    def save(self, *args, **kwargs):
        # Open the uploaded image
        if self.image:
            img = Image.open(self.image)

            # Check if the image is larger than Full HD
            if img.width > 1920 or img.height > 1080:
                # Calculate the new size maintaining the aspect ratio
                max_size = (500, 500)
                img.thumbnail(max_size, Image.LANCZOS)

                # Save the image to a BytesIO object
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG', quality=85)
                img_io.seek(0)

                # Set the image field to the new image
                self.image = InMemoryUploadedFile(
                    img_io, None, self.image.name, 'image/jpeg', img_io.getbuffer().nbytes, None
                )

        super().save(*args, **kwargs)


class GiftLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name='sender_gift', null=True)
    receiver = models.ManyToManyField(CustomUser, related_name='receiver_gift')
    gift = models.ForeignKey(Gift, on_delete=models.SET_NULL, null=True)

    RECEIVER_PLACE_CHOICES = (
        ('LIVE', 'Live'),
        ('CHAT', 'Phòng chat'),
    )
    place = models.CharField(max_length=20, choices=RECEIVER_PLACE_CHOICES, default='LIVE')

    # Gift live_stream
    live_streaming = models.ForeignKey(LiveStreamingHistory, on_delete=models.SET_NULL, null=True)

    amount = models.IntegerField(default=1)
    total_price = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    add_info = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        self.total_price = self.amount * self.gift.price
        super(GiftLog, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Lịch sử tặng quà'
        verbose_name_plural = 'Lịch sử tặng quà'


class Emoji(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(default='', max_length=255)
    image = models.ImageField(upload_to='assets/image/emoji')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmojiLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    emoji = models.ForeignKey(Emoji, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    live = models.ForeignKey(LiveStreamingHistory, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MessageLive(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Người gửi')
    live = models.ForeignKey(LiveStreamingHistory, on_delete=models.CASCADE, null=True, blank=True,
                             verbose_name='Phòng live')

    gift_log = models.ForeignKey(GiftLog, on_delete=models.CASCADE, null=True, blank=True)

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
        ('STICKER', 'Nhãn dán')
    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, null=True, blank=True, verbose_name='Loại')

    text = models.TextField(null=True, blank=True, validators=[JsonWordValidator(banned_words)])
    file = models.ManyToManyField(FileUpload)
    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(auto_now=True)


class BannedUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    live_user = models.ForeignKey(LiveUser, on_delete=models.CASCADE, null=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(auto_now=True)


# =====================   Proxy model ==================================
class LiveChatProxy(LiveStreamingHistory):
    class Meta:
        proxy = True
        verbose_name = 'Phòng Chat'
        verbose_name_plural = 'Phòng Chat'


class LiveAudioProxy(LiveStreamingHistory):
    class Meta:
        proxy = True
        verbose_name = 'Phòng Voice'
        verbose_name_plural = 'Phòng Voice'


class LiveVideoProxy(LiveStreamingHistory):
    class Meta:
        proxy = True
        verbose_name = 'Phòng Video'
        verbose_name_plural = 'Phòng Video'


class LiveStreamProxy(LiveStreamingHistory):
    class Meta:
        proxy = True
        verbose_name = 'Livestream'
        verbose_name_plural = 'Livestream'


class UserGift(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    gift = models.ForeignKey(Gift, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    update_at = models.DateTimeField(auto_now=True)

    def add_quantity(self, quantity):
        self.quantity += quantity
        self.save()

    def sub_quantity(self, quantity):
        self.quantity -= quantity
        self.save()
