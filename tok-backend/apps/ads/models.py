import uuid
from datetime import datetime

from django.db import models
from model_utils import FieldTracker

from api.services.firebase import send_and_save_notification
from apps.general.models import FileUpload
from apps.user.models import CustomUser


class RateCoinPerView(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=255, choices=(
        ('view', 'Xem'),
        ('click', 'Click')
    ), default='view')
    coin = models.FloatField(default=0.1, verbose_name='Số thóc')

    description = models.TextField(default='Số thóc cho 1 lượt hiển thị đến người dùng', verbose_name='Mô tả')
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Cập nhật vào')

    class Meta:
        verbose_name = 'Số thóc 1 lần xem/click'
        verbose_name_plural = 'Số thóc 1 lần xem/click'


class AdsWallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='adswallet', null=True)
    current_balance = models.FloatField(default=0, verbose_name="Số dư ví")
    previous_balance = models.FloatField(default=0)

    tracker = FieldTracker()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def add_balance(self, amount):
        self.previous_balance = self.current_balance
        self.current_balance += amount

        self.save()

    def subtract_balance(self, amount):
        self.previous_balance = self.current_balance
        self.current_balance -= amount
        self.save()

    class Meta:
        verbose_name = "Ví QC"
        verbose_name_plural = "Ví QC"


def target_user():
    return {
        'from_age': 15,
        'to_age': 60,
        'gender': [],
        'country': None,
        'province': [],
        'lat': None,
        'lng': None,
        'distance': None,
        'habit': [],
        'search': [],
        'platform': None
    }


class Advertisement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Người tạo')

    title = models.CharField(max_length=255, verbose_name='Tiêu đề')
    description = models.TextField(verbose_name='Mô tả')

    target_type = models.CharField(max_length=255, choices=(
        ('USER', 'Người dùng'),
        ('WEB', 'Web'),
        ('APP', 'App'),
        ('DEFAULT', 'Mặc định'),
    ), default='DEFAULT', verbose_name='Mục tiêu hướng đến')

    image = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='advertisement_image', null=True,
                              blank=True, verbose_name='Ảnh')
    video = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name='advertisement_video', null=True,
                              blank=True)
    # Web
    direct_url = models.CharField(max_length=300, null=True, blank=True, verbose_name='Link chuyển hướng')

    # App
    android_url = models.CharField(max_length=300, null=True, blank=True, verbose_name='Android link')
    ios_url = models.CharField(max_length=300, null=True, blank=True, verbose_name='IOS Link')
    platform = models.CharField(max_length=255, choices=(
        ('ANDROID', 'Android'),
        ('IOS', 'iOS'),
    ), null=True, blank=True)

    target = models.JSONField(default=target_user)

    is_active = models.BooleanField(default=True)

    status_verify = models.CharField(choices=(
        ('pending', 'Đợi duyệt'),
        ('verified', 'Đã duyệt'),
        ('rejected', 'Đã từ chối'),
    ), default='pending', max_length=10, verbose_name='Trạng thái duyệt')

    status_coming = models.CharField(choices=(
        ('incoming', 'Sắp diễn ra'),
        ('coming', 'Đang diễn ra'),
        ('expired', 'Hết hạn'),
    ), default='incoming', max_length=10, verbose_name='Trạng thái diễn ra')

    coin_price = models.PositiveSmallIntegerField(default=0, verbose_name='Số thóc')
    maximum_view = models.PositiveIntegerField(default=0)

    start_date = models.DateField(null=True, blank=True, verbose_name='Ngày bắt đầu')
    end_date = models.DateField(null=True, blank=True, verbose_name='Ngày kết thúc')

    verified_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verified_ads', null=True,
                                    blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(default='', blank=True, verbose_name='Chú thích tới người dùng')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    @property
    def count_view(self):
        # Tính tổng số lượt xem từ tất cả các AdsTargeting liên quan
        return sum(
            target.count_view for target in self.targets.all()
        )


    @property
    def count_click(self):
        # Tính tổng số lần nhấp từ tất cả các AdsTargeting liên quan
        return sum(
            target.count_click for target in self.targets.all()
        )


    def change_status_coming(self):
        self.status_coming = 'coming'
        self.save()
        send_and_save_notification(user=self.user,
                                   title='Thông báo',
                                   body='Chiến lược quảng bá của bạn đã bắt đầu',
                                   direct_type='ADS_COMING',
                                   direct_value=str(self.id), )

    def change_status_expired(self):
        self.status_coming = 'expired'
        if self.status_verify == 'pending':
            self.note = ('Admin đã thiếu sót trong quá trình kiếm duyệt quảng bá của bạn, vui lòng cập nhật lại hoặc '
                         'liên hệ số hotline')
        self.save()
        send_and_save_notification(user=self.user,
                                   title='Thông báo',
                                   body='Chiến lược quảng bá của bạn đã hết hạn',
                                   direct_type='ADS_EXPIRED',
                                   direct_value=str(self.id), )

    class Meta:
        verbose_name = 'Danh sách quảng bá'
        verbose_name_plural = 'Danh sách quảng bá'


class AdsTargeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    TYPE_CHOICES = (
        ('view', 'Xem'),
        ('click', 'Click'),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='view')

    ads = models.ForeignKey(Advertisement, on_delete=models.CASCADE, related_name='targets')

    viewed_date = models.JSONField(default=dict)
    clicked_date = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def count_view(self):
        # Tính tổng số lượt xem từ tất cả các ngày trong trường viewed_date
        return sum(self.viewed_date.values())

    @property
    def count_click(self):
        # Tính tổng số lần nhấp từ tất cả các ngày trong trường clicked_date
        return sum(self.clicked_date.values())

    def add_view(self):
        today = str(datetime.now().date())
        if today not in self.viewed_date:
            self.viewed_date[today] = 1
        else:
            self.viewed_date[today] += 1

        current_view_rate = RateCoinPerView.objects.get_or_create(key='view',
                                                                  description='Số thóc cho 1 lượt hiển thị đến người dùng')
        wallet = AdsWallet.objects.get_or_create(user=self.ads.user)[0]
        wallet.subtract_balance(current_view_rate[0].coin)
        if wallet.current_balance <= 0:
            self.ads.is_active = False
            self.ads.save()

        self.save()

    def add_click(self):
        self.type = 'click'
        today = str(datetime.now().date())
        if today not in self.clicked_date:
            self.clicked_date[today] = 1
        else:
            self.clicked_date[today] += 1
        current_view_rate = RateCoinPerView.objects.get_or_create(key='click',
                                                                  description='Số thóc cho 1 lượt click từ người dùng')
        wallet = AdsWallet.objects.get_or_create(user=self.ads.user)[0]
        wallet.subtract_balance(current_view_rate[0].coin)
        if wallet.current_balance <= 0:
            self.ads.is_active = False
            self.ads.save()
        self.save()
