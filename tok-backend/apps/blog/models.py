import uuid

from django.db import models

from apps.general.models import FileUpload
from apps.user.models import CustomUser


class AudioUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, null=True, blank=True, verbose_name='Tên hiển thị')
    description = models.TextField(null=True, blank=True)

    index = models.IntegerField(null=True, blank=True, verbose_name='Vị trí hiển thị')

    file = models.FileField(upload_to='assets/blog/audio')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Âm thanh bài đăng'
        verbose_name_plural = 'Âm thanh bài đăng'


class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, default="")
    content = models.TextField(null=True, blank=True, verbose_name="Nội dung")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owner', verbose_name="Người đăng")

    tagged_users = models.ManyToManyField(CustomUser, related_name='tagged_in', blank=True, verbose_name="Gắn thẻ")

    count_comment = models.PositiveIntegerField(default=0, verbose_name="Tổng comment")
    count_like = models.PositiveIntegerField(default=0, verbose_name="Tổng like")
    count_share = models.PositiveIntegerField(default=0, verbose_name="Tổng share")

    location = models.CharField(max_length=50, null=True, blank=True, verbose_name="Vị trí")
    location_point = models.CharField(max_length=50, null=True, blank=True)

    user_like = models.ManyToManyField(CustomUser, blank=True)

    audio = models.ForeignKey(AudioUpload, on_delete=models.SET_NULL, null=True, blank=True)

    file = models.ManyToManyField(FileUpload, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng")
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")
    is_highlight = models.BooleanField(default=False)

    hide_by = models.ManyToManyField(CustomUser, related_name='hide_blog')

    @property
    def bid(self):
        return str(self.id)[-6:].upper()

    def add_hide_by(self, user):
        self.hide_by.add(user)
        self.save()

    class Meta:
        verbose_name = "Bài đăng"
        verbose_name_plural = "Bài đăng"


class LikeBlog(models.Model):
    TYPE_CHOICES = (
        ('LIKE', 'LIKE'),
        ('UNLIKE', 'UNLIKE')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.CharField(choices=TYPE_CHOICES, default='LIKE', max_length=6)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content = models.TextField(null=True, blank=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owner_comment')
    count_like = models.PositiveIntegerField(default=0)

    user_like = models.ManyToManyField(CustomUser, blank=True)
    file = models.ManyToManyField(FileUpload, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class LikeComment(models.Model):
    TYPE_CHOICES = (
        ('LIKE', 'LIKE'),
        ('UNLIKE', 'UNLIKE')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.CharField(choices=TYPE_CHOICES, default='LIKE', max_length=6)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReplyComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    content = models.TextField(null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owner_reply_comment')
    count_like = models.PositiveIntegerField(default=0)
    user_like = models.ManyToManyField(CustomUser, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class LikeReplyComment(models.Model):
    TYPE_CHOICES = (
        ('LIKE', 'LIKE'),
        ('UNLIKE', 'UNLIKE')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    type = models.CharField(choices=TYPE_CHOICES, default='LIKE', max_length=6)
    reply_comment = models.ForeignKey(ReplyComment, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
