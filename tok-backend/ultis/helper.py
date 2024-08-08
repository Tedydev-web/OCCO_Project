import datetime
import os
import re
import uuid
from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db.models import Q
from phonenumbers import is_valid_number, parse
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
import requests
from django.core.files.base import ContentFile
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from apps.conversation.models import Room, RoomUser, Message
from apps.conversation.serializers import MessageSerializer
from apps.general.models import AppConfig

from apps.notification.models import Notification
from apps.user.models import OTP

from apps.user.models import OTP, BaseInformation
from apps.user.serializers import UserFriendShipSerializer

from apps.user.models import OTP

from core import settings
from ultis.socket_helper import send_to_socket, send_noti_to_socket_user, get_socket_data


def validate_email_address(email_address):
    return re.search(r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@[A-Za-z0-9.-]+$", email_address)


def get_validate_date(current_date):
    if current_date:
        return current_date.strftime("%d/%m/%Y")
    else:
        return ''


def get_full_image_url(request, file_path):
    if settings.USE_S3:
        return file_path

    domain = request.META['HTTP_HOST']
    full_url = f"http://{domain}{file_path}"
    return full_url


def convert_phone_number(raw_phone_number):
    # if raw_phone_number[0] == '0':
    #     phone_number = '+84' + raw_phone_number[1:]
    # else:
    #     phone_number = raw_phone_number

    phone_number = parse(raw_phone_number, None)
    is_valid_number(phone_number)

    return phone_number


def custom_user_image_path(instance, filename, path='general'):
    instance_id = str(instance.id)
    upload_path = os.path.join(f'user_media/images/{path}/', instance_id)
    new_filename = f'{uuid.uuid4()}{os.path.splitext(filename)[1]}'
    return os.path.join(upload_path, new_filename)


def is_valid_image(image_field):
    try:
        return image_field and default_storage.exists(image_field.name)
    except:
        return False


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 500
    page_query_param = 'page'

    def __init__(self):
        self.total_record = 0

    def add_total_record(self, total_record):
        self.total_record = total_record

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            # ('total_page', math.ceil(self.page.paginator.count / 10)),
            # ('num_record', len(self.page.object_list)),
            # ('total_record', self.total_record),
            ('current_page', self.page.number),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


def validate_image_format(value):
    if value:
        allowed_formats = ('image/jpeg', 'image/png', 'image/jpg')
        if value.content_type not in allowed_formats:
            raise ValidationError("Invalid image format. Only JPEG and PNG are accepted.")

        if value.size > 5 * 1024 * 1024:  # 5MB file size limit
            raise ValidationError("Image size is too large. The limit is 5MB.")


def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return ContentFile(response.content)
    return None


def convert_unicode_text(text):
    patterns = {
        '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
        '[đ]': 'd',
        '[èéẻẽẹêềếểễệ]': 'e',
        '[ìíỉĩị]': 'i',
        '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
        '[ùúủũụưừứửữự]': 'u',
        '[ỳýỷỹỵ]': 'y'
    }
    """
    Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
    text: input string to be converted
    Return: string converted
    """
    output = text
    for regex, replace in patterns.items():
        output = re.sub(regex, replace, output)
        output = re.sub(regex.upper(), replace.upper(), output)

    return output


def chk_otp_register_send_in_day(phone_number):
    today = datetime.datetime.today().date()
    count_otp = OTP.objects.filter(Q(created_at__date=today) &
                                   (
                                           Q(user__phone_number=phone_number) |
                                           Q(log=phone_number)) &
                                   Q(type='REGISTER')
                                   ).count()
    if count_otp >= int(AppConfig.objects.get(key='MAXIMUM_OTP_DAY').value):
        return False
    return True


def chk_otp_password_send_in_day(phone_number):
    today = datetime.datetime.today().date()
    count_otp = OTP.objects.filter(Q(created_at__date=today) &
                                   (
                                           Q(user__phone_number=phone_number) |
                                           Q(log=phone_number)) &
                                   Q(type='PASSWORD')
                                   ).count()
    if count_otp >= int(AppConfig.objects.get(key='MAXIMUM_OTP_DAY').value):
        return False
    return True


def get_paginator_data(serializer_data, request):
    paginator = CustomPagination()
    result_page = paginator.paginate_queryset(serializer_data, request)
    data = paginator.get_paginated_response(result_page).data
    return data


def get_paginator_limit_offset(query_set, request):
    paginator = LimitOffsetPagination()
    result_page = paginator.paginate_queryset(query_set, request)
    return result_page, paginator


def join_noti_room(user, request):
    room = Room.objects.filter(type='NOTIFICATION', roomuser__user=user).exists()
    if not room:
        room = Room.objects.create(type='NOTIFICATION')
    else:
        room = Room.objects.get(type='NOTIFICATION', roomuser__user=user)

    room.set_newest()
    room_user = RoomUser.objects.get_or_create(user=user, room=room)[0]

    message, created = Message.objects.get_or_create(title='Chào mừng bạn mới',
                                                     text='Chào mừng bạn đến với TOK, cùng trải nghiệm thật nhiều '
                                                          'điều thú vị tại đây nhé.',
                                                     room=room,
                                                     type='TEXT')

    msg_data = MessageSerializer(message, context={'request': request}).data


def send_noti_add_friend(sender, receiver, status):
    # room = Room.objects.filter(type='NOTIFICATION', roomuser__user=receiver).exists()
    # if not room:
    #     room = Room.objects.create(type='NOTIFICATION')
    # else:
    #     room = Room.objects.get(type='NOTIFICATION', roomuser__user=receiver)
    #
    # room_user = RoomUser.objects.get_or_create(user=receiver, room=room)[0]
    #
    # message, created = Message.objects.get_or_create(title='Lời mời kết bạn mới',
    #                                                  text=f'Bạn nhận được lời mời kết bạn từ {sender.full_name}',
    #                                                  room=room,
    #                                                  type='TEXT')
    # notification = Notification(user=sender,
    #                             title=title,
    #                             body=body,
    #                             direct_type=direct_type,
    #                             direct_value=direct_value,
    #                             direct_user=direct_user,
    #                             custom_data=custom_data)
    # notification.save()

    msg_data = {
        'sender': UserFriendShipSerializer(sender).data,
        'receiver': UserFriendShipSerializer(receiver).data,
        'status': status
    }
    # send_to_socket('user', str(room.id), get_socket_data('ADD_FRIEND', msg_data))
    send_noti_to_socket_user(receiver.id, get_socket_data('ADD_FRIEND', msg_data))


def send_noti_accept_friend(sender, receiver, status):
    # room = Room.objects.filter(type='NOTIFICATION', roomuser__user=sender).exists()
    # if not room:
    #     room = Room.objects.create(type='NOTIFICATION')
    # else:
    #     room = Room.objects.get(type='NOTIFICATION', roomuser__user=sender)
    #
    # room_user = RoomUser.objects.get_or_create(user=sender, room=room)[0]
    #
    # message, created = Message.objects.get_or_create(title='Các bạn đã là bạn bè!',
    #                                                  text=f'{receiver.full_name} đã chấp nhận lời mời kết bạn! Bắt'
    #                                                       f' đầu trò chuyện nào!',
    #                                                  room=room,
    #                                                  type='TEXT')

    msg_data = {
        'sender': UserFriendShipSerializer(sender).data,
        'receiver': UserFriendShipSerializer(receiver).data,
        'status': status
    }
    # send_to_socket('user', str(room.id), get_socket_data('ACCEPT_FRIEND', msg_data))
    send_noti_to_socket_user(sender.id, get_socket_data('ACCEPT_FRIEND', msg_data))


def get_list_interest(base_info):
    # Khởi tạo danh sách để lưu trữ các tiêu đề
    title_list = []

    # Lấy tiêu đề từ mỗi mô hình thông tin và thêm vào danh sách
    work_titles = list(base_info.work.all().values_list('title', flat=True))
    title_list.extend(work_titles)

    character_titles = list(base_info.character.all().values_list('title', flat=True))
    title_list.extend(character_titles)

    search_titles = list(base_info.search.all().values_list('title', flat=True))
    title_list.extend(search_titles)

    hobby_titles = list(base_info.hobby.all().values_list('title', flat=True))
    title_list.extend(hobby_titles)

    communicate_titles = list(base_info.communicate.all().values_list('title', flat=True))
    title_list.extend(communicate_titles)

    return title_list


def get_similar_profiles(users, user):
    # Lấy tất cả các hồ sơ người dùng
    all_profiles = BaseInformation.objects.filter(Q(user__in=users) | Q(user=user))

    # Lấy danh sách tất cả các sở thích
    all_interests = []
    for profile in all_profiles:
        interests = get_list_interest(profile)
        all_interests.append(' '.join(interests))

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(all_interests)

    # Tính toán sự tương tự giữa các hồ sơ dựa trên ma trận TF-IDF
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Lấy chỉ số của người dùng hiện tại trong ma trận tương tự
    user_index = all_profiles.filter(user=user).first()

    # Lấy chỉ số của người dùng hiện tại trong danh sách all_profiles
    user_index = list(all_profiles).index(user_index)

    # Lấy các chỉ số của các hồ sơ tương tự
    similar_profile_indices = cosine_similarities[user_index].argsort()[:-5:-1]
    similar_profile_indices = list(similar_profile_indices.astype(int))
    # Lấy danh sách các CustomUser tương tự
    similar_users = [all_profiles[int(i)].user for i in similar_profile_indices if all_profiles[int(i)].user != user]
    return similar_users


def format_currency(amount):
    return f"{int(amount):,}".replace(",", ".")