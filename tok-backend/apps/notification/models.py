import uuid

from django.db import models

from apps.user.models import CustomUser


class UserDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=200, blank=True, unique=True)
    name = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    NOTIFICATION_TYPE = (
        ('SYSTEM', 'Hệ thống'),
        ('FRIEND', 'Bạn bè'),
    )
    type = models.CharField(choices=NOTIFICATION_TYPE, max_length=6, default='SYSTEM')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications', verbose_name='Người nhận')
    title = models.TextField(max_length=80, blank=False, verbose_name="Tiêu đề")
    body = models.TextField(blank=True, null=True, verbose_name="Nội dung")
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    custom_data = models.JSONField(null=True, blank=True)

    direct_type = models.CharField(max_length=100, blank=True)
    direct_value = models.CharField(max_length=200, blank=True)
    direct_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")

    def __str__(self):
        return str(self.id)
    @property
    def nid(self):
        return str(self.id)[-8:].upper()

    def save(self, *args, **kwargs):
        super(Notification, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"
