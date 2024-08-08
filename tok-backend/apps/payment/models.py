import uuid
from django.db import models
from model_utils import FieldTracker

from apps.general.models import Vip
from apps.user.models import CustomUser


class Wallet(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Người dùng",
        related_name='wallet'
    )
    current_balance = models.PositiveIntegerField(
        default=0,
        verbose_name="Số dư ví"
    )
    previous_balance = models.PositiveIntegerField(
        default=0
    )
    tracker = FieldTracker()

    def add_balance(self, amount):
        self.previous_balance = self.current_balance
        self.current_balance += amount
        self.save()

    def subtract_balance(self, amount):
        self.previous_balance = self.current_balance
        self.current_balance -= amount
        self.save()

    class Meta:
        verbose_name = "Ví"
        verbose_name_plural = "Ví"


class Transaction(models.Model):
    FUNDS_CHOICES = [
        ('Coin', 'Thóc'),
        ('Appota', 'Appota')
    ]

    RETURN_CODE_CHOICES = [
        ('00', 'Thành công'),
        ('01', 'Thất bại'),
        ('02', 'Chờ xử lý')
    ]

    TRANSACTION_TYPE_CHOICES = [
        ('deposit', 'Mua thóc'),
        ('uid', 'Mua id'),
        ('avatar', 'Mua khung avatar'),
        ('gift', 'Mua quà'),
        ('withdraw', 'Rút thóc'),
        ('coinToAds', 'Quảng bá'),
        ('vip', 'Mua VIP')
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    amount = models.PositiveIntegerField(
        blank=True,
        default=0,
        verbose_name="Số tiền"
    )
    return_code = models.CharField(
        max_length=2,
        choices=RETURN_CODE_CHOICES,
        blank=True,
        null=True,
        default='02',
        verbose_name="Trạng thái"
    )
    funds = models.CharField(
        max_length=10,
        choices=FUNDS_CHOICES,
        blank=True,
        null=True,
        default='00',
        verbose_name="Nguồn tiền"
    )
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPE_CHOICES,
        default="deposit",
        blank=True,
        null=True,
        verbose_name="Loại giao dịch"
    )
    from_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transaction_from",
        blank=True,
        verbose_name="Người tạo"
    )
    to_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transaction_to",
        blank=True,
        verbose_name="Người nhận"
    )
    information_detail = models.JSONField(
        default=dict,
        verbose_name='Thông tin thêm'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Cập nhật"
    )
    appota_response = models.JSONField(default=dict)
    tracker = FieldTracker()

    @property
    def short_id(self):
        return str(self.id)[-6:].upper()

    def save(self, request=None, *args, **kwargs):
        super().save(*args, **kwargs)

    def add_item_detail(self, data):
        self.information_detail["item_data"] = data
        self.save()

    def add_detail(self, key, data):
        self.information_detail[key] = data
        self.save()

    def add_from_user_data(self, data):
        self.information_detail["from_user_data"] = data
        self.save()

    def add_to_user_data(self, data):
        self.information_detail["to_user_data"] = data
        self.save()

    def add_appota_response(self, data):
        self.appota_response = data
        self.save()

    def update_deposit_status(self, code):
        self.return_code = code
        self.save()

    class Meta:
        verbose_name = 'Giao dịch'
        verbose_name_plural = 'Giao dịch'


class Banking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    bank_code = models.CharField(max_length=256, blank=True, null=True, unique=True)
    bin_card = models.CharField(max_length=256, blank=True, null=True, unique=True)
    filename = models.CharField(max_length=256, blank=True, null=True)

    is_disburse = models.BooleanField(default=False)
    is_napas = models.BooleanField(default=False)
    is_viet_pr = models.BooleanField(default=False)

    fullname = models.TextField(blank=True, null=True, editable=True, verbose_name="Tên ngân hàng")
    short_name = models.CharField(max_length=256, blank=True, null=True, verbose_name="Tên rút gọn", unique=True)
    #   Foreign key
    icon = models.ImageField(upload_to="assets/bank-icon", blank=True, null=True, editable=True, verbose_name="Icon")

    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật")

    class Meta:
        verbose_name = "Ngân hàng"
        verbose_name_plural = "Ngân hàng"

    def __str__(self):
        return self.short_name


class VIPLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Người mua')
    vip = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật")


