import secrets
import uuid
from datetime import datetime, timedelta, date
from itertools import chain

import jwt
import random
import string

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from django.utils.timezone import localtime
from phonenumber_field.modelfields import PhoneNumberField

from django.utils.functional import cached_property

from api.services.stringee import get_access_token
from apps.general.models import FileUpload, DefaultAvatar, AppConfig, AvatarFrame, Vip
from ultis.validate import JsonWordValidator, banned_words


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, **extra_fields):
        if not phone_number:
            raise ValueError('User must have a phone number.')

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(extra_fields.get('password', secrets.token_urlsafe(6)))
        user.save()
        return user

    def create_superuser(self, phone_number, **extra_fields):
        if self.model.objects.filter(phone_number=phone_number).exists():
            raise ValueError('Phone number already exists for a regular user.')

        user = self.create_user(phone_number, **extra_fields)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

    def get_queryset(self):
        return super().get_queryset().select_related('avatar', 'baseinformation').prefetch_related('groups',
                                                                                                   'user_permissions')


class CustomManager(models.Manager):

    def filter_blocked_users(self, request_user):
        blocking = list(request_user.social.get('block', []))
        blocked = list(request_user.social.get('blocked', []))

        return self.exclude(id__in=chain(blocking, blocked)).select_related('avatar')

    def list_friend(self, user):

        return self.filter(id__in=list(user.social.get('friends', []))).select_related('avatar')

    def recommend_users(self, user):
        if not user:
            raise ValueError("Request user is required for RecommendFilter")

        # Get gender and age_range from the request user
        gender = user.gender
        age_range = int(AppConfig.objects.get(key='AGE_RANGE_RECOMMENDED').value)

        # Create an initial filter
        current_filter = Q()

        # Gender filter
        if gender == 'MALE':
            current_filter &= Q(gender='FEMALE')
        elif gender == 'FEMALE':
            current_filter &= Q(gender='MALE')
        else:
            current_filter &= Q(gender=gender)
        id_friend_and_me = chain(list(user.social.get('friends', [])), [str(user.id)])

        gender_qs = self.filter_blocked_users(user).select_related('avatar').prefetch_related('groups',
                                                                                              'user_permissions',
                                                                                              'profileimage_set').filter(
            current_filter).exclude(id__in=id_friend_and_me)

        # Age filter
        age_qs = gender_qs.filter(Q(age__gte=user.age - age_range, age__lte=user.age + age_range))

        # Apply filter to CustomUser queryset
        return age_qs

    def recommend_users_and_weight(self, user):
        if not user:
            raise ValueError("Request user is required for RecommendFilter")

        # Get gender and age_range from the request user
        gender = user.gender
        age_range = int(AppConfig.objects.get(key='AGE_RANGE_RECOMMENDED').value)

        # Create an initial filter
        current_filter = Q()

        # Gender filter
        if gender == 'MALE':
            current_filter &= Q(gender='FEMALE')
        elif gender == 'FEMALE':
            current_filter &= Q(gender='MALE')
        else:
            current_filter &= Q(gender=gender)
        id_friend_and_me = chain(list(user.social.get('friends', [])), [str(user.id)])

        gender_qs = self.filter_blocked_users(user).filter(current_filter).exclude(
            id__in=id_friend_and_me)

        # Age filter
        age_qs = gender_qs.filter(Q(age__gte=user.age - age_range, age__lte=user.age + age_range))
        # print(age_qs)

        weight_qs = age_qs.filter(Q(weight__gte=user.weight - 20, weight__lte=user.weight + 20))

        return weight_qs

    def is_block(self, user1, user2):
        if 'block' in user1.social:
            if str(user2.id) in user1.social['block']:
                return 'BLOCK'
        if 'blocked' in user2.social:
            if str(user1.id) in user2.social['blocked']:
                return 'BLOCKED'
        if 'blocked' in user1.social:
            if str(user2.id) in user1.social['blocked']:
                return 'BLOCKED'
        if 'block' in user2.social:
            if str(user1.id) in user2.social['block']:
                return 'BLOCK'
        return None

    def list_blocking(self, request_user):
        blocking = list(request_user.social.get('block', []))
        blocked = list(request_user.social.get('blocked', []))
        return blocking + blocked


def init_setting():
    return {
        'receive_message_another': True,
        'receive_message_random': True,
        'hide_location': False,
        'hide_recommend_friend': False,
        'hide_match_friend': False,
        'prevent_add_group': False,
        'prevent_add_room': False,
        'prevent_call_another': False
    }


def init_vip():
    return {
        'hide_age': False,
        'hide_gender': False,
        'hide_location': False,
        'prevent_search': False,
        'hide_avt_frame': False,
    }


class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('MALE', 'Nam'),
        ('FEMALE', 'Nữ'),
        ('GAY', 'GAY'),
        ('LESBIAN', 'LESBIAN')
    )
    STATE_CHOICES = (
        ('INFOR', 'INFOR'),
        ('SHARE', 'SHARE'),
        ('DONE', 'DONE')
    )
    # Thông tin cơ bản
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uid = models.CharField(max_length=10, null=True, blank=True)

    full_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Họ và tên",
                                 validators=[JsonWordValidator(banned_words)])
    bio = models.CharField(max_length=500, blank=True, null=True, verbose_name="Bio")
    email = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(unique=True, null=True, verbose_name="Số điện thoại")
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    age = models.IntegerField(null=True, blank=True, verbose_name="Tuổi")
    gender = models.CharField(max_length=7, choices=GENDER_CHOICES, null=True, blank=True, verbose_name="Giới tính")
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name="Chiều cao", default=170)
    weight = models.PositiveIntegerField(null=True, blank=True, verbose_name="Cân nặng", default=59)
    avatar = models.OneToOneField(FileUpload, blank=True, null=True, on_delete=models.DO_NOTHING, related_name="avatar")
    cover_image = models.OneToOneField(FileUpload, blank=True, null=True, on_delete=models.DO_NOTHING,
                                       related_name="cover_image")
    register_status = models.CharField(choices=STATE_CHOICES, null=True, blank=True, max_length=5)

    COUNTRY_CHOICES = (
        ('Vietnam', 'Việt Nam'),
        ('Laos', 'Lào'),
        ('Cambodia', 'Cambodia'),
        ('All', 'Admin tổng'),
    )
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, null=True, blank=True, default="Vietnam",
                               verbose_name='Quốc gia')
    province = models.CharField(max_length=50, null=True, blank=True, default="Hồ Chí Minh", verbose_name='Tỉnh thành')

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    date_joined = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="Ngày tham gia")
    last_update = models.DateField(auto_now=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'

    language_code = models.CharField(max_length=30, default='vi')
    # For check user status
    is_online = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    is_live = models.BooleanField(default=False)
    is_block = models.BooleanField(default=False)
    is_fake = models.BooleanField(default=False, verbose_name='Người dùng ảo')

    # For social
    follower = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    count_friend = models.IntegerField(default=0)

    social = models.JSONField(default=dict)

    # Login social
    google_auth = models.CharField(unique=True, max_length=200, null=True, blank=True)
    apple_auth = models.CharField(unique=True, max_length=200, null=True, blank=True)

    # For live
    agoraUID = models.TextField(null=True, blank=True)
    stringeeUID = models.TextField(null=True, blank=True)

    # Private account
    is_private = models.BooleanField(default=False)
    is_upload_idcard = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True, verbose_name='Có quyền truy cập')
    is_verify = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    # Filter
    custom_objects = CustomManager()
    NOTIFICATION_CHOICES = (
        ('on', 'Bật thông báo'),
        ('off23to6', 'Tắt 23h đến 6h'),
        ('off', 'Tắt thông báo'),
    )
    notification_mode = models.CharField(default='on', choices=NOTIFICATION_CHOICES)

    #
    avatar_frame = models.ForeignKey(AvatarFrame, on_delete=models.SET_NULL, null=True, blank=True)

    #
    setting_private = models.JSONField(default=init_setting)
    setting_vip = models.JSONField(default=init_vip)
    # Platform
    platform = models.CharField(choices=(
        ('ANDROID', 'ANDROID'),
        ('IOS', 'IOS')
    ), default='ANDROID', max_length=10)

    @property
    def date(self):
        return localtime(self.date_joined).strftime('%H:%M %d/%m/%Y')

    def __str__(self):
        return self.full_name if self.full_name else ''

    def check_vip(self, data):
        if self.setting_vip.get('hide_gender', None):
            data['gender'] = None
        if self.setting_vip.get('hide_location',None):
            data['distance'] = None
        if self.setting_vip.get('hide_avt_frame', None):
            data['avatar_frame'] = None
        if self.setting_vip.get('hide_age', None):
            data['age'] = None
        data['setting_vip'] = self.setting_vip
        return data

    def save(self, *args, **kwargs):
        # Default date_of_birth if not provided
        if not self.date_of_birth:
            self.date_of_birth = date(2000, 1, 1)

        # Calculate age
        age = (timezone.now().date() - self.date_of_birth).days // 365
        self.age = int(age)

        if self.uid is None:
            self.uid = str(self.id)[-8:].upper()
        super(CustomUser, self).save(*args, **kwargs)

    @cached_property
    def get_avatar(self):
        if self.avatar is None:
            return str(DefaultAvatar.objects.get(key='avatar').image.url)

        return str(self.avatar.file.url)

    @cached_property
    def get_avatar_frame(self):
        if self.avatar_frame is not None:
            return str(self.avatar_frame.frame.url)

        return None

    @property
    def get_cover_image(self):
        if self.cover_image is None:
            return str(DefaultAvatar.objects.get(key='avatar').image.url)

        return str(self.cover_image.file.url)

    @cached_property
    def player_avatar(self):
        html = '<img src="{img}" style="max-width: 100px; height: auto; display: block; margin: 0 auto;">'
        if self.avatar:
            return format_html(html, img=self.avatar.url)
        return format_html('<strong>There is no image for this entry.<strong>')

    player_avatar.short_description = 'Avatar'

    @property
    def new_password(self):
        new_pwd = secrets.token_urlsafe(6)
        self.set_password(new_pwd)
        self.save()
        return new_pwd

    @property
    def token(self):
        dt = datetime.now() + timedelta(days=60)
        token = jwt.encode({
            'id': str(self.pk),
            'exp': int(dt.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')
        return token

    @property
    def raw_phone_number(self):
        return str(self.phone_number) if self.phone_number else ""

    def set_online(self, online):
        self.is_online = online
        self.save()
        # try:
        #     if self.is_online:
        #         send_noti_online_to_friend.s(uid=str(self.id)).apply_async(countdown=0)
        # except Exception as e:
        #     print(e)

    def new_stringee_token(self):
        self.stringeeUID = get_access_token(str(self.id))[0]
        self.save()

    # ============== Friend list ============= #
    def plus_count_friend(self, id):
        id = str(id)

        # Cập nhật list_friend với friend_id
        if 'friends' not in self.social:
            self.social['friends'] = {}

        if id not in self.social['friends']:
            self.social['friends'][id] = {
                'added_at': datetime.now().isoformat()
            }
            self.count_friend = len(self.social['friends'])
            # Lưu lại thay đổi
            self.save()
            # print(self.social['friends'], self.count_friend)

    def minus_count_friend(self, id):
        id = str(id)

        # Kiểm tra xem friend_id có tồn tại trong list_friend không
        if 'friends' in self.social and id in self.social['friends']:
            # Xóa friend_id khỏi social
            del self.social['friends'][id]

            # Giảm số lượng bạn bè
            self.count_friend = len(self.social['friends'])
            # Lưu lại thay đổi
            self.save()

    # ============== Friend request list ========= #
    def plus_friend_request(self, id):
        id = str(id)

        # Cập nhật list_friend với friend_id
        if 'friend_request' not in self.social:
            self.social['friend_request'] = {}

        if id not in self.social['friend_request']:
            self.social['friend_request'][id] = {
                'added_at': datetime.now().isoformat()
            }
        # Lưu lại thay đổi
        self.save()

    def minus_friend_request(self, id):
        id = str(id)

        # Kiểm tra xem friend_id có tồn tại trong list_friend không
        if 'friend_request' in self.social and id in self.social['friend_request']:
            # Xóa friend_id khỏi social
            del self.social['friend_request'][id]

            # Lưu lại thay đổi
            self.save()

    # ============== Friend accept ============= #
    def plus_friend_accept(self, id):
        id = str(id)

        # Cập nhật list_friend với friend_id
        if 'friend_accept' not in self.social:
            self.social['friend_accept'] = {}

        if id not in self.social['friend_accept']:
            self.social['friend_accept'][id] = {
                'added_at': datetime.now().isoformat()
            }
        # Lưu lại thay đổi
        self.save()

    def minus_friend_accept(self, id):
        id = str(id)

        # Kiểm tra xem friend_id có tồn tại trong list_friend không
        if 'friend_accept' in self.social and id in self.social['friend_accept']:
            # Xóa friend_id khỏi social
            del self.social['friend_accept'][id]

            # Lưu lại thay đổi
            self.save()

    # ============== Block list ================ #
    def add_blocking(self, id):
        id = str(id)

        if 'block' not in self.social:
            self.social['block'] = {}

        if id not in self.social['block']:
            self.social['block'][id] = {
                'added_at': datetime.now().isoformat()
            }

        # Lưu lại thay đổi
        self.save()

    def remove_relationship(self, id):
        id = str(id)
        if 'following' in self.social and id in self.social['following']:
            del self.social['following'][id]
            self.following = len(self.social['following'])

        if 'follower' in self.social and id in self.social['follower']:
            del self.social['follower'][id]
            self.follower = len(self.social['follower'])

        if 'friend_request' in self.social and id in self.social['friend_request']:
            # Xóa friend_id khỏi social
            del self.social['friend_request'][id]

        if 'friend_accept' in self.social and id in self.social['friend_accept']:
            # Xóa friend_id khỏi social
            del self.social['friend_accept'][id]

        if 'friends' in self.social and id in self.social['friends']:
            # Xóa friend_id khỏi social
            del self.social['friends'][id]

            # Giảm số lượng bạn bè
            self.count_friend = len(self.social['friends'])
            # Lưu lại thay đổi
        self.save()

    def remove_blocking(self, id):
        id = str(id)

        if 'block' in self.social and id in self.social['block']:
            del self.social['block'][id]

            self.save()

    def add_blocked(self, id):
        id = str(id)

        if 'blocked' not in self.social:
            self.social['blocked'] = {}

        if id not in self.social['blocked']:
            self.social['blocked'][id] = {
                'added_at': datetime.now().isoformat()
            }

        # Lưu lại thay đổi
        self.save()

    def remove_blocked(self, id):
        id = str(id)

        if 'blocked' in self.social and id in self.social['blocked']:
            del self.social['blocked'][id]

            self.save()

    def add_following(self, id):
        id = str(id)

        if 'following' not in self.social:
            self.social['following'] = {}

        if id not in self.social['following']:
            self.social['following'][id] = {
                'added_at': datetime.now().isoformat()
            }
            self.following = len(self.social['following'])

        # Lưu lại thay đổi
        self.save()

    def remove_following(self, id):
        id = str(id)

        if 'following' in self.social and id in self.social['following']:
            del self.social['following'][id]
            self.following = len(self.social['following'])
            self.save()

    def add_follower(self, id):
        id = str(id)

        if 'follower' not in self.social:
            self.social['follower'] = {}

        if id not in self.social['follower']:
            self.social['follower'][id] = {
                'added_at': datetime.now().isoformat()
            }
            self.follower = len(self.social['follower'])

        # Lưu lại thay đổi
        self.save()

    def remove_follower(self, id):
        id = str(id)

        if 'follower' in self.social and id in self.social['follower']:
            del self.social['follower'][id]
            self.follower = len(self.social['follower'])
            self.save()

    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"


class ReportMessage(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name='Người vi phạm')
    count = models.IntegerField(default=0, verbose_name='Số lần')

    banned_to = models.DateTimeField(null=True, blank=True, verbose_name='Bị cấm đến')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def new_verified_report(self):
        self.count += 1
        msg = (f'Bạn đã vi phạm quy chế và điều khoản của chúng tôi khi nhắn tin {self.count} lần.\n Nếu vi phạm quá 3 '
               f'lần, bạn sẽ bị cấm nhắn tin trong 1 ngày.')
        if self.count == 3:
            self.banned_to = datetime.now()

        elif self.count > 3:
            self.banned_to = datetime.now() + timedelta(days=int(self.count - 3))
            # msg = f"Bạn đã vi phạm qui tắc phòng chat {self.count} lần và bị cấm chat đến {self.banned_to.strftime('%H:%M:%S %d/%m/%Y')}"
            msg = f"Bạn đã bị cấm nhắn tin đến {self.banned_to.strftime('%H:%M:%S %d/%m/%Y')} do vi phạm quy chế và điều khoản của chúng TOK."
        else:
            ...
        self.save()
        return msg

    def check_banned(self):
        if self.banned_to < datetime.now():
            return False, self.banned_to.strftime('%H:%M:%S %d/%m/%Y')
        return True, self.banned_to.strftime('%H:%M:%S %d/%m/%Y')

    class Meta:
        verbose_name = 'Vi phạm tin nhắn'
        verbose_name_plural = 'Vi phạm tin nhắn'


class WorkInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Nghề nghiệp"
        verbose_name_plural = "Nghề nghiệp"


class CharacterInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Tích cách"
        verbose_name_plural = "Tích cách"


class SearchInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Tìm kiếm"
        verbose_name_plural = "Tìm kiếm"


class HobbyInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Sở thích"
        verbose_name_plural = "Sở thích"


class CommunicateInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Nhu cầu"
        verbose_name_plural = "Nhu cầu"


class RelatedBaseInformation(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('user').prefetch_related('search', 'work', 'character', 'hobby',
                                                                              'communicate')


class BaseInformation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    search = models.ManyToManyField(SearchInformation, verbose_name="Tìm kiếm", blank=True)
    work = models.ManyToManyField(WorkInformation, verbose_name="Công việc", blank=True)
    character = models.ManyToManyField(CharacterInformation, verbose_name="Tính cách", blank=True)
    hobby = models.ManyToManyField(HobbyInformation, verbose_name="Sở thích", blank=True)
    communicate = models.ManyToManyField(CommunicateInformation, verbose_name="Nhu cầu", blank=True)

    objects = RelatedBaseInformation()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Thông tin"
        verbose_name_plural = "Thông tin"

    @property
    def habits(self):
        lst_search = list(self.search.all().values_list('id', flat=True))
        lst_hobby = list(self.hobby.all().values_list('id', flat=True))
        return lst_search + lst_hobby


class OTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    code = models.CharField(max_length=6, blank=True)
    log = models.TextField(blank=True, default="")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    TYPE_CHOICES = (
        ('REGISTER', 'Đăng ký'),
        ('PASSWORD', 'Quên mật khẩu'),
    )
    type = models.CharField(max_length=8, choices=TYPE_CHOICES, null=True, blank=True)

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=2)

    @property
    def short_id(self):
        return str(self.id)[-6:].upper()

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        self.code = self.generate_otp()
        super().save(*args, **kwargs)


class LetterAvatar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=10, blank=True)
    image = models.ImageField(upload_to='letter-avatar-images')


class ProfileImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ForeignKey(FileUpload, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ảnh profile'
        verbose_name_plural = 'Ảnh profile'


class FriendShip(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Đã gửi lời mời kết bạn'),  # Đã gửi lời kết bạn đang đợi phản hồi
        ('ACCEPTED', 'Đang là bạn bè'),  # Đã chấp nhận lời mời kết bạn => đang là bạn bè
        ('REJECTED', 'Từ chối kết bạn'),  # Đã bị từ chối kết bạn
        ('DELETED', 'Đã xóa')  # Đã xóa bạn bè
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='receiver')
    status = models.CharField(choices=STATUS_CHOICES, default='PENDING', max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f"{self.sender.full_name} - {self.receiver.full_name}: {self.status}"


class Block(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    STATUS_CHOICES = (
        ('BLOCK', 'Block'),
        ('UNBLOCK', 'Unblock')
    )
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default='BLOCK')

    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
                                  related_name='user_block')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='user_blocked')

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def set_status(self, status):
        self.status = status
        self.save()


class Follow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_follower')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_followed')

    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class UserLog(models.Model):
    user = models.CharField(unique=True, max_length=100)
    phone_number = models.CharField()
    info = models.JSONField(default=list)
    login = models.JSONField(default=list)
    logout = models.JSONField(default=list)
    blog = models.JSONField(default=list)
    live = models.JSONField(default=list)
    comment = models.JSONField(default=list)


class IDCard(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, related_name='id_card')
    id_front_image = models.ImageField(upload_to='assets/id-card/front-image/', null=True)
    id_back_image = models.ImageField(upload_to='assets/id-card/back-image/', null=True)
    id_face_image = models.ImageField(upload_to='assets/id-card/face-image/', null=True)
    STATUS_CHOICES = (
        ('start', 'Chưa nộp'),
        ('pending', 'Đợi duyệt'),
        ('verified', 'Đã duyệt'),
        ('rejected', 'Đã từ chối'),
    )
    status_verify = models.CharField(max_length=10, choices=STATUS_CHOICES, default='start',
                                     verbose_name='Trạng thái duyệt')
    id_full_name = models.CharField(max_length=255, null=True, blank=True)
    GENDER_CHOICES = (
        ('male', 'Nam'),
        ('female', 'Nữ'),
    )
    id_gender = models.CharField(max_length=7, choices=GENDER_CHOICES, null=True)
    id_identifier = models.CharField(max_length=255, null=True, blank=True)
    id_date_of_birth = models.CharField(max_length=255, null=True, blank=True)
    id_date_issuance = models.CharField(max_length=255, null=True, blank=True)
    id_place_of_residence = models.CharField(max_length=255, null=True, blank=True)
    verified_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='id_verified',
                                    verbose_name='Duyệt bởi')
    verified_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'CCCD'
        verbose_name_plural = 'CCCD'


class UserTimeline(models.Model):
    TYPE_CHOICES = (
        ('COMMENT', 'COMMENT'),
        ('LIKE', 'LIKE'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Người dùng tạo thông báo', related_name='timeline')

    direct_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name='Người liên quan', related_name='related_timeline')

    type = models.CharField(choices=TYPE_CHOICES, default='', max_length=50)
    fk_id = models.CharField(null=True, blank=True, max_length=255)
    title = models.TextField(max_length=80, blank=False, verbose_name="Tiêu đề")
    body = models.TextField(blank=True, null=True, verbose_name="Nội dung")
    link = models.CharField(max_length=1000, default="/admin")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class HistorySeen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    user_seen = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='seen_page')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserVip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vip')
    vip = models.ForeignKey(Vip, on_delete=models.SET_NULL, null=True, related_name='users')

    date_start = models.DateTimeField(null=True, blank=True)
    date_end = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Cập nhật")
