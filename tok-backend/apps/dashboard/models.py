import uuid

from django.db import models

from apps.user.models import CustomUser


class FCMToken(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.token


class NotificationAdmin(models.Model):
    TYPE_CHOICES = (
        ('COMMENT', 'COMMENT'),
        ('LIKE', 'LIKE'),
        ('REFLECT', 'REFLECT'),
        ('NEW', 'NEW')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    from_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                  verbose_name='Người dùng tạo thông báo', related_name='notification_admin_user')
    type = models.CharField(choices=TYPE_CHOICES,default='',max_length=50)

    title = models.TextField(max_length=80, blank=False, verbose_name="Tiêu đề")
    body = models.TextField(blank=True, null=True, verbose_name="Nội dung")
    link = models.CharField(max_length=1000, default="/admin")
    admin_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='notification_admin',
                                   verbose_name='Thông báo cho admin')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True)
