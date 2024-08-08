import os
from datetime import datetime
from functools import partial

from colorfield.fields import ColorField
from django.db import models
import uuid

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.settings import AUTH_USER_MODEL
from ultis.file_helper import custom_media_file_path, format_file_size


# Create your models here.
class HomeContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="", null=True, blank=True, verbose_name="Tiêu đề")
    introduce_content = models.TextField(blank=True, null=True, verbose_name="Nội dung giới thiệu")
    terms_content = models.TextField(blank=True, null=True, verbose_name="Nội dung chính")
    image = models.ImageField(upload_to='assets/homecontent', null=True, blank=True, verbose_name="Ảnh")


class AppConfig(models.Model):
    key = models.CharField(max_length=50, default="", blank=True, primary_key=True, verbose_name="Tên")
    value = models.TextField(default="", blank=True, null=True, verbose_name="Giá trị")
    note = models.TextField(default="", blank=True, verbose_name="Chú thích")
    created_at = models.DateTimeField(auto_now_add=True, null=True, editable=False, verbose_name="Thiết lập ngày")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật ngày")

    class Meta:
        verbose_name = "Giá trị mặc định"
        verbose_name_plural = "Giá trị mặc định"


class AboutUs(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    description = models.TextField("Nội dung", blank=True)

    @property
    def short_description(self):
        return f'{str(self.description)[:50]}...'

    class Meta:
        verbose_name = "Hướng dẫn"
        verbose_name_plural = "Hướng dẫn"


class PrivateTerms(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    description = models.TextField('Nội dung', blank=True)

    @property
    def short_description(self):
        return f'{str(self.description)[:50]}...'

    class Meta:
        verbose_name = "Điều khoản & Điều kiện"
        verbose_name_plural = "Điều khoản & Điều kiện"


class FileUpload(models.Model):
    FILE_TYPE_CHOICE = (
        ('IMAGE', 'Ảnh'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('FILE', 'File')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                              verbose_name='Người upload')

    media_path = partial(custom_media_file_path, path="media")
    file = models.FileField(upload_to=media_path, null=True, blank=True)

    file_url = models.CharField(null=True, blank=True, max_length=500)
    file_type = models.CharField(choices=FILE_TYPE_CHOICE, null=True, blank=True, max_length=500)
    file_name = models.TextField(default='', null=True, blank=True, max_length=500, verbose_name='Tên file')
    file_extension = models.CharField(null=True, blank=True, max_length=500)
    file_size = models.CharField(null=True, blank=True, max_length=500)

    upload_finished_at = models.DateTimeField(blank=True, null=True)
    file_duration = models.PositiveIntegerField(default=0, null=True, blank=True)

    video_height = models.PositiveIntegerField(default=0)
    video_width = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày đăng')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name or ''  # Ensure it returns a string

    def save(self, *args, **kwargs):
        if self.file:
            self.file_name = self.file.name.split('/')[-1]
            self.file_url = self.file.url
            self.file_extension = os.path.splitext(self.file_name)[1]
            try:
                self.file_size = format_file_size(self.file.size)
            except:
                self.file_size = 0
        super().save(*args, **kwargs)


@receiver(post_save, sender=FileUpload)
def update_end_time(sender, instance, **kwargs):
    if instance.upload_finished_at is None:
        instance.upload_finished_at = datetime.now()
        instance.save()


class OTPRequest(models.Model):
    class Meta:
        verbose_name = "OTP History"
        verbose_name_plural = "OTP Histories"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=50, editable=False)
    otp = models.CharField(max_length=50, editable=False)
    return_code = models.CharField(max_length=2, default="", blank="")
    info = models.TextField(default="", blank="")
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.phone_number} - {self.otp} - {self.info}'


class DevSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    config = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_time_queue(cls):
        # Lấy đối tượng DevSetting, hoặc tạo mới nếu chưa tồn tại
        dev_setting, created = cls.objects.get_or_create(pk=1)
        # Lấy giá trị của key 'time_queue' trong config, mặc định là 60 nếu không có
        time_queue = dev_setting.config.get('time_queue', 60)
        return int(time_queue)

    @classmethod
    def get_value(cls, key):
        dev_setting, created = cls.objects.get_or_create(pk=1)
        value = dev_setting.config.get(key)
        return value


class DefaultAvatar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key = models.CharField(max_length=15, null=True, blank=True)
    image = models.ImageField(upload_to='assets/default/avatar', default='constants/default_avatar.png')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FeedBack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name='Người gửi')

    full_name = models.CharField(max_length=255, null=True, verbose_name='Họ tên')
    phone_number = models.CharField(max_length=255, null=True, verbose_name='Số điện thoại')
    description = models.TextField(null=True, blank=True, verbose_name='Mô tả')

    is_resolve = models.BooleanField(default=False, verbose_name='Đã xử lý')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phản hồi'
        verbose_name_plural = 'Phản hồi'

    @property
    def fid(self):
        return str(self.id)[-6:].upper()


class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    REPORT_TYPE = (
        ('MESSAGE', 'Tin nhắn'),
        ('BLOG', 'Bài đăng'),
        ('LIVE', 'Live')
    )
    type = models.CharField(max_length=7, choices=REPORT_TYPE, null=True, blank=True, verbose_name='Loại')

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_sender',
                             verbose_name='Người gửi')
    direct_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
                                    verbose_name="Người bị tố cáo", related_name='report_receiver')

    fk_id = models.CharField(max_length=255, null=True, blank=True, verbose_name='id')
    content = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nội dung')
    image = models.ManyToManyField(FileUpload, verbose_name='Bằng chứng')

    is_verified = models.BooleanField(default=False, verbose_name='Đã duyệt')
    note = models.CharField(default='', verbose_name='Lí do duyệt', max_length=500)
    verifier = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='report_verifier', verbose_name='Người duyệt')

    created_at = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật ngày")

    def __str__(self):
        return f"Report by {self.user} - {self.type}"  # Ensure this returns a string

    class Meta:
        verbose_name = 'Tố cáo'
        verbose_name_plural = 'Tố cáo'


class BackGroundColor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    color = models.CharField(default='#FF0000', verbose_name='Mã màu')
    title = models.CharField(default='Màu', verbose_name='Tên màu')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Màu nền chat'
        verbose_name_plural = 'Màu nền chat'


class CoinTrading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    coin_price = models.PositiveIntegerField(default=0, verbose_name='Số thóc')
    vnd_price = models.PositiveIntegerField(default=0, verbose_name='VNĐ')

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quy đổi tiền sang thóc'
        verbose_name_plural = 'Quy đổi tiền sang thóc'


class MoneyTrading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, null=True, blank=True)
    coin_price = models.PositiveIntegerField(default=0, verbose_name='Số thóc')
    vnd_price = models.PositiveIntegerField(default=0, verbose_name='VNĐ')

    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quy đổi thóc sang tiền'
        verbose_name_plural = 'Quy đổi thóc sang tiền'


class UIDTrading(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uid = models.CharField(max_length=8, verbose_name='UID', unique=True)
    coin_price = models.PositiveIntegerField(default=0, verbose_name='Số thóc')

    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Danh sách UID'
        verbose_name_plural = 'Danh sách UID'


class StickerCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='images/stickers/', null=True, blank=True)

    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    index = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bộ nhãn dán'
        verbose_name_plural = 'Bộ nhãn dán'


class Sticker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='assets/stickers/', null=True, blank=True, )

    sticker_category = models.ForeignKey(StickerCategory, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')

    index = models.PositiveSmallIntegerField(default=0, verbose_name='Vị trí hiển thị')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FileUploadAudio(FileUpload):
    class Meta:
        proxy = True
        verbose_name = 'Quản lý audio'
        verbose_name_plural = 'Quản lý audio'


class AvatarFrame(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, null=True, blank=True)
    frame = models.FileField(upload_to='assets/avatar-frame/', null=True, blank=True)

    coin_price = models.PositiveIntegerField(default=0, verbose_name='Số thóc')

    is_active = models.BooleanField(default=True, verbose_name='Trạng thái hoạt động')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Khung avatar'
        verbose_name_plural = 'Khung avatar'


class Vip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    coin_price = models.PositiveIntegerField(default=0, verbose_name='Số thóc')
    total_month = models.PositiveIntegerField(default=1, verbose_name='Số tháng')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Gói VIP'
        verbose_name_plural = 'Gói VIP'


class AppInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key = models.CharField(max_length=255, choices=(
        ('instruction', 'Hướng dẫn'),
        ('aboutUs', 'Về OCCO'),
        ('rule', 'Điều khoản đăng ký'),
        ('appInfo', 'Thông tin về ứng dụng')
    ), null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='ID')
    value = models.TextField(null=True, blank=True, verbose_name='Nội dung')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Thông tin ứng dụng'
        verbose_name_plural = 'Thông tin ứng dụng'


class SupportAndTraining(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='assets/support-training/', null=True, blank=True)

    index = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Hỗ trợ và đào tạo'
        verbose_name_plural = 'Hỗ trợ và đào tạo'
        ordering = ['index', ]
