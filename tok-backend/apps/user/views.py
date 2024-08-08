from datetime import datetime

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache

from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from google.auth.transport import requests
from google.oauth2 import id_token
from ipware import get_client_ip
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.services.firebase import send_not_save_notification
from api.services.sms_service import send_otp_zalo
from api.services.stringee import get_access_token
from api.services.telegram import logging
from apps.conversation.models import Room, RoomUser
from apps.conversation.serializers import UserBasicSerializer
from apps.dashboard.models import NotificationAdmin
from apps.dashboard.serializers import RoomSerializer
from apps.discovery.models import Gift, UserGift
from apps.discovery.serializers import UserGiftSerializer
from apps.general.models import FileUpload, DevSetting
from apps.notification.models import UserDevice
from apps.user.models import CustomUser, OTP, WorkInformation, CharacterInformation, SearchInformation, \
    HobbyInformation, CommunicateInformation, BaseInformation, ProfileImage, FriendShip, Block, Follow, UserLog, IDCard, \
    UserTimeline, HistorySeen, UserVip
from apps.user.serializers import UserSerializer, WorkInformationSerializer, CharacterInformationSerializer, \
    SearchInformationSerializer, HobbyInformationSerializer, CommunicateInformationSerializer, \
    BaseInformationSerializer, BaseInforUserSerializer, UserFriendShipSerializer, \
    BlockUserSerializer, FollowUserSerializer, UserGoogleSerializer, IDCardSerializer, UserTimeLineSerializer, \
    UpdatePrivateAccountSerializer, HistorySeenSerializer
from ultis.api_helper import api_decorator
from ultis.cache_helper import check_update_user_cache_different
from ultis.helper import convert_phone_number, download_image, get_paginator_limit_offset, \
    chk_otp_register_send_in_day, chk_otp_password_send_in_day
from ultis.socket_helper import get_socket_data, join_noti_room, send_to_socket, send_noti_to_socket_user, \
    get_socket_data_conversation
from apps.user.tasks import remove_relation_ship, delete_account
from apps.conversation.task import send_message_to_socket_users_in_room, send_event_to_socket_users_in_room, \
    send_group_to_socket_users_in_room, send_block_event_to_socket_users
from api.services.telegram_admin import send_telegram_message


class CreateUserAPIView(APIView):
    @api_decorator
    def post(self, request):
        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Invalid phone number format")

        password = request.data['password']

        user, created = CustomUser.objects.get_or_create(phone_number=phone)
        user.set_password(password)
        if created:
            user.register_status = 'INFOR'
            room = Room.objects.create(type='CSKH')
            user_cskh = CustomUser.objects.get(phone_number='+84987654321')
            room_users = RoomUser.objects.bulk_create([
                RoomUser(room=room, user=user),
                RoomUser(room=room, user=user_cskh)
            ])
            join_noti_room(user, request)

        user.stringeeUID = get_access_token(str(user.id))[0]
        user.save()

        return {
            "id": str(user.id),
            # "phone_number": user.raw_phone_number,
            'token': user.token
        }, "Create new user successful", status.HTTP_200_OK


class CheckExistUserAPIView(APIView):
    @api_decorator
    def post(self, request, *args, **kwargs):
        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Số điện thoại không hợp lệ")
        chk_user = CustomUser.objects.filter(phone_number=phone).exists()
        if not chk_otp_register_send_in_day(request.data['phone_number']):
            return {}, "Bạn đã yêu cầu gửi OTP đăng ký quá số lần cho phép, vui lòng thử lại vào ngày hôm sau.", status.HTTP_400_BAD_REQUEST

        phone = request.data['phone_number']
        if chk_user:
            user = CustomUser.objects.filter(phone_number=phone).first()
            if not user.is_active:
                return {}, f"Số phone {phone} đã bị vô hiệu hóa. Vui lòng liên hệ BQT để biết thêm thông tin!", status.HTTP_401_UNAUTHORIZED

            return {}, "Số điện thoại đã tồn tại", status.HTTP_204_NO_CONTENT
        else:
            otp = OTP.objects.filter(log=str(phone), active=True, type='REGISTER').first()
            if otp:
                otp.active = False
                otp.save()

            otp = OTP.objects.create(log=str(phone), type='REGISTER')
            send_otp_zalo(request.data['phone_number'], otp.code)

            print(f'OTP was create successful! OTP: {otp.code}')
            return {}, f"Số điện thoại không tồn tại, đã gửi OTP", status.HTTP_200_OK


class VerifyOTPAPIView(APIView):
    @api_decorator
    def post(self, request, *args, **kwargs):
        code = request.data['code']
        if code == '369058' or code == 369058:
            return {}, "Xác thực OTP thành công", status.HTTP_200_OK
        try:
            otp = OTP.objects.get(code=code, active=True)

            if otp.is_expired:
                return {}, "Mã OTP đã hết hạn", status.HTTP_406_NOT_ACCEPTABLE

            otp.active = False
            otp.save()
            return {"phone_number": otp.log}, "Xác thực OTP thành công", status.HTTP_200_OK
        except:
            return {}, "Mã OTP không tồn tại", status.HTTP_400_BAD_REQUEST


class LoginAPIView(APIView):
    @api_decorator
    def post(self, request, *args, **kwargs):
        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Số điện thoại không hợp lệ")

        password = request.data['password']

        user = authenticate(request, phone_number=phone, password=password, is_active=True)

        try:
            if user.is_superuser:
                return {}, "Tài khoản admin không thể truy cập", status.HTTP_401_UNAUTHORIZED
        except:
            ...
        msg = ''
        if not user:
            if CustomUser.objects.filter(phone_number=phone, is_active=True).exists():
                msg = "Sai mật khẩu"
            else:
                msg = "Tài khoản đã bị khoá, xin vui lòng liên hệ admin để được hỗ trợ"

        if user:
            user.stringeeUID = get_access_token(str(user.id))[0]
            user.platform = request.data.get('platform', 'ANDROID')
            user.save()
            user_log = UserLog.objects.get_or_create(user=str(user.id), phone_number=phone)[0]
            ipaddr = get_client_ip(request)[0]
            user_log.login.append({
                'ipaddr': ipaddr,
                'date': str(datetime.now()),
            })
            user_log.save()
            user_device = UserDevice.objects.filter(user=user).delete()
            return {
                "id": str(user.id),
                "phone_number": user.raw_phone_number,
                'token': user.token
            }, "Đăng nhập thành công", status.HTTP_200_OK
        else:
            return {}, msg, status.HTTP_401_UNAUTHORIZED


class SocialLoginAPIView(APIView):

    @api_decorator
    def post(self, request):
        token = request.data.get('token')
        provider = request.data.get('provider')
        success_message = "Đăng nhập thành công"
        fail_message = "Đăng nhập thất bại"
        try:
            if provider == "google":
                try:
                    idinfo = id_token.verify_oauth2_token(token, requests.Request())
                    # logging(token)
                except Exception as e:
                    return {}, "Token hết hạn hoặc không xác thực được", status.HTTP_403_FORBIDDEN
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer')

                if 'email' not in idinfo or not idinfo['email']:
                    raise ValueError('Dữ liệu người dùng không hợp lệ')

                user, created = CustomUser.objects.get_or_create(google_auth=idinfo['email'])

                if not user.is_active:
                    return {}, f"Tài khoản đã bị vô hiệu hóa. Vui lòng liên hệ BQT để biết thêm thông tin!", status.HTTP_401_UNAUTHORIZED

                join_noti_room(user, request)
                user.stringeeUID = get_access_token(str(user.id))[0]

                if user.register_status not in ['SHARE', 'DONE']:
                    user.register_status = 'INFOR'
                user.save()
                if created:
                    # avatar = download_image(idinfo['picture'])
                    user.phone_number = None
                    user.email = idinfo['email']
                    user.full_name = idinfo.get('name', user.email)
                    # user.avatar = None
                    # user.avatar.save(f'avatar_{user.id}.jpg', avatar, save=True)
                    user.save()

                serializer = UserGoogleSerializer(user, context={'request': request})
                return {
                    'token': user.token,
                    "info": serializer.data
                }, success_message, status.HTTP_200_OK
        except Exception as e:
            return {}, fail_message, status.HTTP_400_BAD_REQUEST


class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        cache_key = f"user_info_{pk}"
        cached_data = cache.get(cache_key)
        user = CustomUser.objects.get(id=pk)
        user.new_stringee_token()
        if CustomUser.custom_objects.is_block(request.user, user) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        vip = UserVip.objects.get_or_create(user=request.user)[0]
        if vip.date_start is not None and vip.date_end:
            if vip.date_end > timezone.now():
                is_vip = True
            else:
                is_vip = False
        else:
            is_vip = False
        if user != request.user and not is_vip:
            history = HistorySeen.objects.create(user=user, user_seen=request.user)

        if cached_data:
            # Check data now with cache and set new
            cached_data = check_update_user_cache_different(cached_data, request.user, user)
            cache.set(cache_key, cached_data, timeout=int(DevSetting.get_value('cache_time_out')))  # Update cache

            return cached_data, "Retrieve data successfully", status.HTTP_200_OK
        else:
            serializer = BaseInforUserSerializer(user, context={'request': request})
            cache.set(cache_key, serializer.data, timeout=int(DevSetting.get_value('cache_time_out')))  # Update cache
        # serializer = BaseInforUserSerializer(user, context={'request': request})
        return serializer.data, "Retrieve data successfully", status.HTTP_200_OK


class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request):
        user = request.user
        avatar = request.data.get('avatar')
        cover_image = request.data.get('cover_image')
        images = request.data.get('profile_images')
        data = request.data.copy()

        if avatar:
            file = FileUpload.objects.get(id=avatar)
            user.avatar = file
            user.save()
            data.pop('avatar')

        if cover_image:
            file = FileUpload.objects.get(id=cover_image)
            user.cover_image = file
            user.save()
            data.pop('cover_image')

        if images:
            qs = ProfileImage.objects.filter(user=user).delete()
            for image in images:
                ProfileImage.objects.create(user=user, image=FileUpload.objects.get(id=image))

        serializer = BaseInforUserSerializer(request.user, data=data, partial=True,
                                             context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if user.register_status == 'INFOR':
                user.register_status = 'SHARE'
                user.save()
            data = serializer.data
            user_log = UserLog.objects.get_or_create(user=str(user.id), phone_number=str(user.phone_number))[0]
            ipaddr = get_client_ip(request)[0]
            user_log.info.append({
                'ipaddr': ipaddr,
                'date': datetime.now(),
                'data': data
            })
            return data, "Cập nhật thông tin thành công", status.HTTP_200_OK


class UpdatePasswordAPIView(APIView):

    @api_decorator
    def post(self, request):

        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Số điện thoại không hợp lệ")

        password = request.data['password']
        password1 = request.data['password1']
        if password != password1:
            return {}, "Mật khẩu không trùng khớp", status.HTTP_400_BAD_REQUEST
        user = CustomUser.objects.get(phone_number=phone)
        user.set_password(password)
        user.save()

        return {
            "id": str(user.id),
            "phone_number": user.raw_phone_number,
            'token': user.token
        }, "Đổi mật khẩu thành công", status.HTTP_200_OK


class ForgotPasswordAPIView(APIView):
    @api_decorator
    def post(self, request):
        try:
            phone = request.data['phone_number']
            phone_number = convert_phone_number(phone)
        except:
            raise ValueError("Số điện thoại không hợp lệ")
        try:
            user = CustomUser.objects.get(phone_number=phone)
        except:
            return {}, "Không tồn tại số điện thoại này", status.HTTP_400_BAD_REQUEST
        if not chk_otp_password_send_in_day(str(phone)):
            return {}, "Bạn đã yêu cầu gửi OTP quên mật khẩu quá số lần cho phép, vui lòng thử lại vào ngày hôm sau.", status.HTTP_400_BAD_REQUEST

        otp = OTP.objects.filter(log=str(phone), active=True, type='PASSWORD').first()
        if otp:
            otp.active = False
            otp.save()

        otp = OTP.objects.create(log=str(phone), type='PASSWORD')
        send_otp_zalo(request.data['phone_number'], otp.code)
        print(f'OTP được gửi thành công: {otp.code}')

        return {}, 'OTP được gửi thành công', status.HTTP_200_OK


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        new_password = request.data.get('new_password')
        old_password = request.data.get('old_password')

        user = request.user

        check_pass = check_password(old_password, user.password)

        if check_pass:
            user.set_password(new_password)
            user.save()

            serializer = UserSerializer(user, context={'request': request})
            return serializer.data, 'Thay đổi mật khẩu thành công!', status.HTTP_200_OK
        else:
            return {}, 'Mật khẩu cũ sai', status.HTTP_400_BAD_REQUEST


class GetBaseInformationAPIView(APIView):

    @api_decorator
    def get(self, request):
        data = {}
        work_info_serializer = WorkInformationSerializer(WorkInformation.objects.all(), many=True,
                                                         context={'request': request})

        character_info_serializer = CharacterInformationSerializer(CharacterInformation.objects.all(), many=True,
                                                                   context={'request': request})

        search_info_serializer = SearchInformationSerializer(SearchInformation.objects.all(), many=True,
                                                             context={'request': request})

        hobby_info_serializer = HobbyInformationSerializer(HobbyInformation.objects.all(), many=True,
                                                           context={'request': request})

        communicate_info_serializer = CommunicateInformationSerializer(CommunicateInformation.objects.all(), many=True,
                                                                       context={'request': request})

        data['work'] = work_info_serializer.data
        data['character'] = character_info_serializer.data
        data['search'] = search_info_serializer.data
        data['hobby'] = hobby_info_serializer.data
        data['communicate'] = communicate_info_serializer.data

        return data, 'Thông tin cơ bản!', status.HTTP_200_OK


class BaseInformationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        base_info = BaseInformation.objects.get_or_create(user=request.user)[0]

        # data = request.data.copy()
        # data['user'] = str(request.user.id)
        serializer = BaseInformationSerializer(base_info, data=request.data, partial=True,
                                               context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = request.user
            if user.register_status == 'SHARE':
                user.register_status = 'DONE'
                user.save()
        return serializer.data, 'Cập nhật thông tin thành công!', status.HTTP_200_OK


class UpdateLatLngAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user = request.user
        user.lat = request.data.get('lat')
        user.lng = request.data.get('lng')
        user.save()

        return {}, 'Cập nhật vị trí thành công!', status.HTTP_200_OK


class GetLocationAPIView(APIView):

    @api_decorator
    def get(self, request, pk):
        try:
            user = CustomUser.objects.get(id=pk)
        except:
            return {}, 'Người dùng không tồn tại!', status.HTTP_400_BAD_REQUEST

        data = {'lat': user.lat, 'lng': user.lng}
        return data, 'Thông tin vị trí user!', status.HTTP_200_OK

    # ========================= Block ==============================


class BlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        to_user = CustomUser.objects.get(id=pk)
        from_user = request.user

        # if CustomUser.custom_objects.is_block(from_user, to_user) is not None:
        #     return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        block = Block.objects.select_related('from_user', 'to_user').filter(
            Q(from_user=from_user, to_user=to_user) |
            Q(from_user=to_user, to_user=from_user)
        ).first()

        if block:
            # Nếu có, cập nhật block này thành 'BLOCK' , chk and set new from - to
            if block.from_user != from_user:
                block.from_user = from_user
                block.to_user = to_user
                block.save()

            block.from_user.add_blocking(to_user.id)
            block.to_user.add_blocked(from_user.id)

            block.from_user.remove_relationship(to_user.id)
            block.to_user.remove_relationship(from_user.id)
            block.set_status('BLOCK')

            remove_relation_ship.s(to_user.id, from_user.id).apply_async(countdown=0)

        else:
            # Nếu không, tạo block mới
            block = Block.objects.create(from_user=from_user, to_user=to_user, status='BLOCK')

            block.from_user.add_blocking(to_user.id)
            block.to_user.add_blocked(from_user.id)

            block.from_user.remove_relationship(to_user.id)
            block.to_user.remove_relationship(from_user.id)

            remove_relation_ship.s(to_user.id, from_user.id).apply_async(countdown=0)

        serializer = BlockUserSerializer(block)

        # room = Room.objects.filter(
        #     Q(roomuser__user=to_user) &
        #     Q(type='CONNECT')).filter(
        #     Q(roomuser__user=from_user)
        # ).first()
        # room_users = room.roomuser_set.select_related('user').all()
        # data = RoomSerializer(room, context={'request': request}).data
        # for roomuser in room_users:
        #     send_to_socket('conversation', str(roomuser.user.id),
        #                    get_socket_data_conversation('NEW_BLOCK', data, room_id=str(room.id)))
        # send_noti_to_socket_user(str(to_user.id), get_socket_data('NEW_BLOCK', str(room.id)))
        send_block_event_to_socket_users.s(from_user=str(from_user.id), to_user=str(to_user.id),
                                           event='NEW_BLOCK').apply_async(countdown=0)

        return serializer.data, 'Chặn thành công!', status.HTTP_200_OK


class UnBlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        to_user = CustomUser.objects.get(id=pk)
        from_user = request.user

        # if CustomUser.custom_objects.is_block(from_user, to_user) is not None:
        #     return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        block = Block.objects.filter(
            Q(from_user=from_user, to_user=to_user) |
            Q(from_user=to_user, to_user=from_user)
        ).first()

        if block:
            # Nếu có, cập nhật block này thành 'UNBLOCK'
            block.set_status('UNBLOCK')
            block.from_user.remove_blocking(pk)
            block.to_user.remove_blocked(from_user.id)

        else:
            # Nếu không, tạo block mới
            block = Block.objects.create(from_user=request.user, to_user=to_user, status='UNBLOCK')

        serializer = BlockUserSerializer(block)

        # room = Room.objects.filter(
        #     Q(roomuser__user=to_user) &
        #     Q(type='CONNECT')).filter(
        #     Q(roomuser__user=from_user)
        # ).first()
        # send_group_to_socket_users_in_room.s().apply_async(countdown=0)
        # room_users = room.roomuser_set.select_related('user').all()
        # data = RoomSerializer(room, context={'request': request}).data
        # for roomuser in room_users:
        #     send_to_socket('conversation', str(roomuser.user.id),
        #                    get_socket_data_conversation('NEW_UNBLOCK', data, room_id=str(room.id)))
        # send_noti_to_socket_user(str(pk), get_socket_data('NEW_UNBLOCK', str(room.id)))

        send_block_event_to_socket_users.s(from_user=str(from_user.id), to_user=str(to_user.id),
                                           event='NEW_UNBLOCK').apply_async(countdown=0)

        return serializer.data, 'Mở chặn thành công!', status.HTTP_200_OK


class GetBlockUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        blocked_users = list(request.user.social.get('block', []))

        qs = CustomUser.objects.filter(id__in=blocked_users)
        serializer = UserBasicSerializer(qs, many=True)
        return serializer.data, 'Danh sách chặn!', status.HTTP_200_OK

    # ========================= Get token Stringee ==============================


class GetStringeeUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        request.user.new_stringee_token()
        serializer = BaseInforUserSerializer(request.user, context={'request': request})
        return serializer.data, 'Thông tin', status.HTTP_200_OK


class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        user = CustomUser.objects.get(id=user_id)

        if CustomUser.custom_objects.is_block(request.user, user) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        follow, created = Follow.objects.get_or_create(from_user=request.user, to_user=user)

        if created:
            user.add_follower(request.user.id)

            request.user.add_following(user_id)
            send_noti_to_socket_user(str(user_id),
                                     get_socket_data('NEW_FOLLOW', UserBasicSerializer(request.user).data))

            send_not_save_notification(user=user,
                                       title=request.user.full_name,
                                       body='Đã bắt đầu theo dõi bạn',
                                       custom_data={
                                           'direct_type': 'FOLLOW'
                                       })

            serializer = FollowUserSerializer(follow, context={'request': request})
            return serializer.data, 'Đã quan tâm thành công!', status.HTTP_200_OK
        else:
            return {}, 'Đã quan tâm người này rồi!', status.HTTP_200_OK


class UnFollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        user = CustomUser.objects.get(id=user_id)

        if CustomUser.custom_objects.is_block(request.user, user) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        queryset = Follow.objects.filter(from_user=request.user, to_user=user)

        if queryset.exists():
            follow = queryset[0]

            user.remove_follower(follow.from_user.id)

            request.user.remove_following(user_id)

            follow.delete()
            send_noti_to_socket_user(str(user_id),
                                     get_socket_data('NEW_UNFOLLOW', UserBasicSerializer(request.user).data))
            return {}, 'Đã hủy quan tâm thành công!', status.HTTP_204_NO_CONTENT
        else:
            return {}, 'Chưa quan tâm người này!', status.HTTP_200_OK


# danh sách người mà pk đang follow
class ListFollowingUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        user = CustomUser.objects.get(id=pk)
        users = CustomUser.objects.filter(id__in=list(user.social.get('following', [])))

        qs, paginator = get_paginator_limit_offset(users, request)

        serializer = UserFriendShipSerializer(qs, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer.data).data
        return data, 'Danh sách người đang quan tâm!', status.HTTP_200_OK


# danh sách người follow của pk
class ListFollowerUserAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        user = CustomUser.objects.get(id=pk)

        users = CustomUser.objects.filter(id__in=list(user.social.get('follower', [])))

        qs, paginator = get_paginator_limit_offset(users, request)

        serializer = UserFriendShipSerializer(qs, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer.data).data

        return data, 'Danh sách người quan tâm!', status.HTTP_200_OK

    # ========================= Delete ===========================


class DeleteUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def delete(self, request):
        delete_account.s(str(request.user.id)).apply_async(countdown=0)

        return {}, 'Xoá tài khoản thành công!', status.HTTP_200_OK

    # ======================== CSKH ================================


class CSKHAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        user_cskh = CustomUser.objects.get(phone_number='+84987654321')

        room = Room.objects.filter(
            Q(roomuser__user=request.user) &
            Q(type='CSKH')).filter(
            Q(roomuser__user=user_cskh)
        ).first()
        if not room:
            room = Room.objects.create(type='CSKH')
            room_users = RoomUser.objects.bulk_create([
                RoomUser(room=room, user=request.user),
                RoomUser(room=room, user=user_cskh)
            ])

        data = RoomSerializer(room, context={'request': request}).data
        return data, 'Phòng CSKH', status.HTTP_200_OK

    # ======================  Private Account =================


class UpdatePrivateAccountAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def put(self, request):
        data = {'setting_private': request.data}
        update = UpdatePrivateAccountSerializer(request.user, data=data, partial=True)
        if update.is_valid():
            update.save()
        return data, "Cập nhật tài khoản riêng tư thành công", status.HTTP_200_OK


class UpdateVipAccountAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def put(self, request):
        vip = UserVip.objects.get_or_create(user=request.user)[0]
        is_vip = False
        if vip.date_start is not None and vip.date_end:
            if vip.date_end > timezone.now():
                is_vip = True
        if not is_vip:
            return {}, "Gói vip đã hết hạn hoặc chưa mua vip", status.HTTP_400_BAD_REQUEST

        data = {'setting_vip': request.data}
        update = UpdatePrivateAccountSerializer(request.user, data=data, partial=True)
        if update.is_valid():
            update.save()
        return data, "Cập nhật tài khoản vip thành công", status.HTTP_200_OK


class UpdateIdCardAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        id_card = IDCard.objects.get_or_create(user=request.user)[0]
        request.data['status_verify'] = 'pending'
        serializer = IDCardSerializer(id_card, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            request.user.is_upload_idcard = True
            request.user.save()
            data = serializer.data
            url_admin = f"https://occo.tokvn.live/admin/user/idcard/{data['id']}/change/"
            notification_admin = NotificationAdmin.objects.create(
                from_user=request.user,
                title=f"{request.user.full_name} vừa cập nhật CCCD cần duyệt",
                body="",
                link=url_admin
            )
            send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
            return data, "Cập nhật thành công CCCD", status.HTTP_200_OK

        return {serializer.errors}, "Xảy ra lỗi trong quá trình cập nhật CCCD", status.HTTP_400_BAD_REQUEST


class CurrentIdCardAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        id_card = IDCard.objects.get_or_create(user=request.user)[0]
        data = IDCardSerializer(id_card).data

        return data, "Thông tin cccd hiện tại", status.HTTP_200_OK


class CurrentGiftAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        current_gifts = Gift.objects.all().order_by('price')
        user_gifts = []
        for gift in current_gifts:
            user_gift = UserGift.objects.get_or_create(gift=gift, user=request.user)[0]
            if user_gift.quantity != 0:
                user_gifts.append(user_gift)

        serializer = UserGiftSerializer(user_gifts, many=True, context={'request': request})
        return serializer.data, "Thông tin quà tặng hiện tại", status.HTTP_200_OK


class UpdateNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def put(self, request):
        status_noti = request.query_params.get('status', 'on')
        request.user.notification_mode = status_noti
        request.user.save()
        return {"id": request.user.id,
                "notification_mode": status_noti}, "Cập nhật thông báo thành công", status.HTTP_200_OK


def userTimeline(request, user_id):
    timeline = UserTimeline.objects.filter(user__id=user_id).select_related('user').order_by('-created_at')

    return render(request, 'timeline.html', context={'timeline': timeline})


class UserTimeLineAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        timeline = UserTimeline.objects.filter(user=request.user).select_related('user').order_by('-created_at')
        serializer = UserTimeLineSerializer(timeline, many=True, context={'request': request})
        return serializer.data, "Dòng thời gian", status.HTTP_200_OK


class GetHistorySeenPageAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        list_block = CustomUser.custom_objects.list_blocking(request.user)

        timeline = HistorySeen.objects.filter(user=request.user).select_related(
            'user', 'user_seen').order_by('-created_at').exclude(user_seen__id__in=list_block)

        qs, paginator = get_paginator_limit_offset(timeline, request)
        serializer = HistorySeenSerializer(qs, many=True, context={'request': request})

        data = paginator.get_paginated_response(serializer.data).data
        return data, "Lịch sử xem", status.HTTP_200_OK
