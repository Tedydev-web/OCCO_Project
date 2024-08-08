import uuid
from datetime import datetime

from django.contrib.postgres.lookups import Unaccent
from django.db.models import Q, Func, F
from ipware import get_client_ip
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from api.services.agora.main import get_token_subscriber
from api.services.firebase import send_not_save_notification
from api.services.telegram_admin import send_telegram_message
from apps.dashboard.models import NotificationAdmin
from apps.discovery.task import send_new_message_to_live, send_new_join_leave_to_live, send_action_from_user_to_live, \
    send_emoji_to_live, send_gift_to_live, send_action_from_host_to_user_in_live, send_new_live_to_user, \
    send_new_update_live, send_from_host_to_user_in_live
from apps.general.models import AppConfig, FileUpload, Sticker
from apps.discovery.models import LiveUser, LiveStreamingHistory, Gift, MessageLive, GiftLog, Emoji, EmojiLog, UserGift
from apps.discovery.serializers import LiveStreamingSerializer, UserLiveViewSerializer, GiftSerializer, \
    MessageLiveSerializer, GiftLogSerializer, EmojiSerializer, EmojiLogSerializer, LiveUserSerializer, \
    ListLiveSerializer, LiveUpdateSerializer
from apps.payment.models import Wallet, Transaction
from apps.user.models import CustomUser, UserLog
from ultis.api_helper import api_decorator
from ultis.helper import get_paginator_data, get_paginator_limit_offset
from ultis.socket_helper import send_to_socket, get_socket_data


#   =========================  Host LiveStreaming ==========================
class HostCreateLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        room_id = request.data.get('id', None)
        if room_id is not None:
            if LiveStreamingHistory.objects.filter(id_show=room_id).exists():
                id_new = LiveStreamingHistory.objects.create()
                id_return = str(id_new.id)[-10:].upper()
                id_new.delete()
                return id_return, "Đã tồn tại id này, gợi ý id mới", status.HTTP_400_BAD_REQUEST

        type_live = request.data.get('type', None)
        room_name = request.data.get('name', '')
        cover_image = request.data.get('cover_image', None)
        description = request.data.get('description', None)
        max_chairs = request.data.get('max_chairs', 9)
        user = request.user

        live_history_count = LiveStreamingHistory.objects.filter(host=user, type=type_live).count()
        # if live_history_count >= int(AppConfig.objects.get(key='MAXIMUM_CHAT_ROOM').value):
        #     return {}, "Đã quá số phòng trò chuyện tối đa cho phép tạo", status.HTTP_400_BAD_REQUEST
        if cover_image:
            cover_image = FileUpload.objects.get(id=cover_image)
        live = LiveStreamingHistory.objects.create(host=user, type=type_live, name=room_name,
                                                   id_show=room_id, cover_image=cover_image, description=description,
                                                   max_chairs=max_chairs)
        # Create live user and change is_online in room
        live_user = LiveUser.objects.create(user=user, live_streaming=live)
        live_user.set_role('HOST')
        live_user.set_live(True)
        live_user.join_room()

        live.add_view(live_user)

        serializer = LiveStreamingSerializer(live)
        data = serializer.data
        send_new_live_to_user.s(str(live.id), data).apply_async(countdown=0)
        if live.type == 'AUDIO':
            model = 'liveaudioproxy'
        elif live.type == 'VIDEO':
            model = 'livevideoproxy'
        else:
            model = 'livestreamproxy'

        url_admin = f"https://occo.tokvn.live/admin/discovery/{model}/{str(live.id)}/change/"
        notification_admin = NotificationAdmin.objects.create(
            from_user=request.user,
            title=f"{request.user.full_name} vừa tạo phòng {live.type} mới",
            body=f"với ID: {live.id_show}",
            type="NEW",
            link=url_admin
        )
        send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
        user_log = UserLog.objects.get_or_create(user=str(user.id), phone_number=str(user.phone_number))[0]
        ipaddr = get_client_ip(request)[0]
        user_log.live.append({
            'ipaddr': ipaddr,
            'date': str(datetime.now()),
            'data': data
        })
        user_log.save()
        return data, "Tạo phòng live thành công", status.HTTP_200_OK


class HostUpdateLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def put(self, request, pk):
        live = LiveStreamingHistory.objects.get(id=pk)
        serializer = LiveUpdateSerializer(live, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            send_new_update_live.s(str(live.id), data).apply_async(countdown=0)

            return data, "Update phòng live thành công", status.HTTP_200_OK
        else:
            return {}, "Có lỗi xảy ra", status.HTTP_400_BAD_REQUEST


class HostRemoveLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def delete(self, request, pk):
        live = LiveStreamingHistory.objects.get(id=pk)
        live.delete()
        return {}, "Xoá phòng thành công", status.HTTP_200_OK


class HostChooseUserToKeyAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        live_id = request.data.get('live_id', None)
        user_id = request.data.get('user_id', None)
        live_user = LiveUser.objects.get(live_streaming__id=live_id,
                                         user__id=user_id)
        live_user.set_role('KEY')
        send_action_from_host_to_user_in_live.s(live_id=live_id,
                                                live_user_id=str(live_user.id),
                                                event='NEW_MEMBER_KEY').apply_async(countdown=0)
        return {}, 'Chỉ định người dùng lên phó phòng thành công', status.HTTP_200_OK


class HostChooseUserToMemberAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        live_id = request.data.get('live_id', None)
        user_id = request.data.get('user_id', None)
        live_user = LiveUser.objects.get(live_streaming__id=live_id,
                                         user__id=user_id)
        live_user.set_role('USER')
        send_action_from_host_to_user_in_live.s(live_id=live_id,
                                                live_user_id=str(live_user.id),
                                                event='NEW_KEY_REMOVE').apply_async(countdown=0)
        return {}, 'Thu hồi người dùng phó phòng thành công', status.HTTP_200_OK


class HostKickUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        live_id = request.data.get('live_id', None)
        user_id = request.data.get('user_id', None)
        live_user = LiveUser.objects.get(live_streaming__id=live_id,
                                         user__id=user_id)

        live = LiveStreamingHistory.objects.get(id=live_id)
        live.less_view(live_user)

        live_user.is_active = False
        live_user.save()
        send_action_from_host_to_user_in_live.s(live_id=str(live.id),
                                                live_user_id=str(live_user.id),
                                                event='NEW_KICK').apply_async(countdown=0)

        return {}, "Đã đuổi người dùng ra khỏi phòng", status.HTTP_200_OK


class HostKickUserChairAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        live_id = request.data.get('live_id', None)
        user_id = request.data.get('user_id', None)
        live_user = LiveUser.objects.get(live_streaming__id=live_id,
                                         user__id=user_id)
        live_user.set_live(False)
        send_action_from_host_to_user_in_live.s(live_id=live_id,
                                                live_user_id=str(live_user.id),
                                                event='NEW_KICK_CHAIR').apply_async(countdown=0)
        return {}, "Đã cho người dùng xuống ghế", status.HTTP_200_OK


class HostStopLiveAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        live = LiveStreamingHistory.objects.filter(id=pk, host__id=request.user.id).first()
        if not live:
            return {}, "Bạn không phải là chủ phòng hoặc phiên live không tồn tại", status.HTTP_400_BAD_REQUEST

        live.is_stopped = True
        live.save()

        send_from_host_to_user_in_live.s(live_id=str(pk),
                                         event='LIVE_ENDED').apply_async(countdown=0)
        return {}, "Đã dừng phiên live", status.HTTP_200_OK


class ListMyLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        qs = LiveStreamingHistory.objects.select_related('host').filter(host=request.user, is_hide=False).exclude(
            type='STREAM',
            is_stopped=True).order_by('-started_at')
        serializer = LiveStreamingSerializer(qs, many=True)
        return serializer.data, "Danh sách phòng live của tôi", status.HTTP_200_OK


#   =========================  Join LiveStreaming ==========================

class UserJoinLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        try:
            live = LiveStreamingHistory.objects.filter(id=pk, is_stopped=False).first()
            if live is None:
                return {}, "Phiên live không tồn tại", status.HTTP_400_BAD_REQUEST
        except Exception as e:
            return e, "Phiên live không tồn tại", status.HTTP_400_BAD_REQUEST
        live_user, created = LiveUser.objects.get_or_create(user=request.user,
                                                            live_streaming=live)

        if not live_user.is_active:
            return {}, "Bạn không thể tham gia phòng này do có hành vi không phù hợp", status.HTTP_400_BAD_REQUEST

        if created:
            live_user.set_role('USER')

        # Change online in room
        live_user.join_room()
        # Add user to live
        live.add_view(live_user)

        serializer = LiveStreamingSerializer(live)

        msg = MessageLive(type='JOIN',
                          text=f"{request.user.full_name} vừa tham gia phòng live",
                          sender=request.user,
                          live=live,
                          )
        msg.save()  # Lưu đối tượng vào cơ sở dữ liệu
        send_new_message_to_live.s(str(live.id), str(msg.id)).apply_async(countdown=0)

        send_new_join_leave_to_live.s(live_id=str(live.id),
                                      live_user_id=str(live_user.id),
                                      event='NEW_JOIN').apply_async(countdown=0)
        data = serializer.data
        data['agora_token'] = get_token_subscriber(str(pk), str(request.user.id))
        return data, 'Tham gia live thành công!', status.HTTP_200_OK


class UserJoinChairStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        try:
            live = LiveStreamingHistory.objects.get(id=pk)
        except Exception as e:
            return e, "Phiên live không tồn tại", status.HTTP_400_BAD_REQUEST

        try:
            live_user, created = LiveUser.objects.get_or_create(user=request.user,
                                                                live_streaming=live)
        except:
            return {}, "Bạn không thể tham gia phòng này do có hành vi không phù hợp", status.HTTP_400_BAD_REQUEST
        if created:
            live_user.set_role('USER')

        # Change online in room
        live_user.join_room()
        live_user.set_live(True)

        # Add user to live
        live.add_view(live_user)
        msg = MessageLive(type='CHAIR',
                          text=f"{request.user.full_name} vừa lên ghế",
                          sender=request.user,
                          live=live,
                          )
        msg.save()  # Lưu đối tượng vào cơ sở dữ liệu
        send_new_message_to_live.s(str(live.id), str(msg.id)).apply_async(countdown=0)
        serializer = LiveStreamingSerializer(live)
        send_new_join_leave_to_live.s(live_id=str(live.id),
                                      live_user_id=str(live_user.id),
                                      event='NEW_JOIN_CHAIR').apply_async(countdown=0)
        return serializer.data, 'Tham gia live thành công!', status.HTTP_200_OK


class UserLeaveLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        live = LiveStreamingHistory.objects.get(id=pk)
        live_user, created = LiveUser.objects.get_or_create(user=request.user,
                                                            live_streaming=live)
        # Change online status in live
        live_user.leave_room()
        # Remove user in live
        live.less_view(live_user)
        live_user.set_live(False)
        serializer = LiveStreamingSerializer(live)
        send_new_join_leave_to_live.s(live_id=str(live.id),
                                      live_user_id=str(live_user.id),
                                      event='NEW_LEAVE').apply_async(countdown=0)
        return serializer.data, 'Rời live thành công!', status.HTTP_200_OK


class UserLeaveChairStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        live = LiveStreamingHistory.objects.get(id=pk)

        live_user, created = LiveUser.objects.get_or_create(user=request.user,
                                                            live_streaming=live)
        if not live_user.is_active:
            return {}, "Bạn không thể tham gia phòng này do có hành vi không phù hợp", status.HTTP_400_BAD_REQUEST

        # Change online status in live
        live_user.leave_room()
        live_user.set_live(False)

        # Remove user in live
        # live.less_view(live_user)

        serializer = LiveStreamingSerializer(live)
        send_new_join_leave_to_live.s(live_id=str(live.id),
                                      live_user_id=str(live_user.id),
                                      event='NEW_LEAVE_CHAIR').apply_async(countdown=0)

        return serializer.data, 'Rời ghế thành công!', status.HTTP_200_OK


class UserRecentlyJoinLiveStreamAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        qs = LiveStreamingHistory.objects.select_related('host', 'cover_image'
                                                         ).filter(liveuser__user=request.user,
                                                                  is_stopped=False).order_by(
            '-liveuser__last_join').exclude(
            liveuser__role='HOST',
            liveuser__is_online=False
        )

        serializer = LiveStreamingSerializer(qs, many=True)

        return serializer.data, 'Danh sách gần đây!', status.HTTP_200_OK


#   =========================  List LiveStreaming ==========================
class GetListLiveChatAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        qs = LiveStreamingHistory.objects.select_related('cover_image').defer('view').filter(type='CHAT',
                                                                                             is_stopped=False,
                                                                                             is_hide=False)

        side = request.query_params.get('side')
        if side:
            qs = qs.filter(side=side)

        serializer = ListLiveSerializer(qs, many=True)
        return serializer.data, "Danh sách phòng conversation", status.HTTP_200_OK


class GetListLiveVoiceAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        people_sort = request.query_params.get('people_sort', 'asc')
        time_sort = request.query_params.get('time_sort', 'desc')
        qs = LiveStreamingHistory.objects.select_related('cover_image').defer('view').filter(type='AUDIO',
                                                                                             is_stopped=False,
                                                                                             is_hide=False).exclude(
            liveuser__role='HOST',
            liveuser__is_online=False
        )

        if people_sort == 'asc' and time_sort == 'desc':
            qs = qs.order_by('user_view', '-started_at')
        elif people_sort == 'desc' and time_sort == 'desc':
            qs = qs.order_by('-user_view', 'started_at')
        elif people_sort == 'desc' and time_sort == 'asc':
            qs = qs.order_by('-user_view', '-started_at')
        else:
            qs = qs.order_by('user_view', 'started_at')

        qs, paginator = get_paginator_limit_offset(qs, request)
        serializer = ListLiveSerializer(qs, many=True)
        data_paginator = paginator.get_paginated_response(serializer.data).data

        return data_paginator, "Danh sách phòng voice", status.HTTP_200_OK


class GetListLiveVideoAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        people_sort = request.query_params.get('people_sort', 'asc')
        time_sort = request.query_params.get('time_sort', 'desc')
        qs = LiveStreamingHistory.objects.select_related('cover_image').defer('view').filter(type='VIDEO',
                                                                                             is_hide=False).exclude(
            liveuser__role='HOST',
            liveuser__is_online=False
        )

        if people_sort == 'asc' and time_sort == 'desc':
            qs = qs.order_by('user_view', '-started_at')
        elif people_sort == 'desc' and time_sort == 'desc':
            qs = qs.order_by('-user_view', 'started_at')
        elif people_sort == 'desc' and time_sort == 'asc':
            qs = qs.order_by('-user_view', '-started_at')
        else:
            qs = qs.order_by('user_view', 'started_at')

        qs, paginator = get_paginator_limit_offset(qs, request)
        serializer = ListLiveSerializer(qs, many=True)
        data_paginator = paginator.get_paginated_response(serializer.data).data
        return data_paginator, "Danh sách phòng stream", status.HTTP_200_OK


class GetListLiveStreamAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        people_sort = request.query_params.get('people_sort', 'asc')
        time_sort = request.query_params.get('time_sort', 'desc')
        qs = LiveStreamingHistory.objects.select_related('cover_image').defer('view').filter(type='STREAM',
                                                                                             is_stopped=False,
                                                                                             is_hide=False)

        if people_sort == 'asc' and time_sort == 'desc':
            qs = qs.order_by('user_view', '-started_at')
        elif people_sort == 'desc' and time_sort == 'desc':
            qs = qs.order_by('-user_view', 'started_at')
        elif people_sort == 'desc' and time_sort == 'asc':
            qs = qs.order_by('-user_view', '-started_at')
        else:
            qs = qs.order_by('user_view', 'started_at')

        qs, paginator = get_paginator_limit_offset(qs, request)
        serializer = ListLiveSerializer(qs, many=True)
        data_paginator = paginator.get_paginated_response(serializer.data).data
        return data_paginator, "Danh sách phòng stream", status.HTTP_200_OK


class GetListViewerAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request, pk):
        qs_user = LiveUser.objects.filter(live_streaming__id=pk, is_online=True, role='USER').values_list('user',
                                                                                                          flat=True)
        qs_key = LiveUser.objects.filter(live_streaming__id=pk, is_online=True, role='KEY').values_list('user',
                                                                                                        flat=True)
        qs_user = CustomUser.objects.filter(id__in=qs_user)
        qs_key = CustomUser.objects.filter(id__in=qs_key)
        live = LiveStreamingHistory.objects.get(id=pk)
        host = live.host
        data_user = UserLiveViewSerializer(qs_user, many=True).data
        data_key = UserLiveViewSerializer(qs_key, many=True).data
        data_host = UserLiveViewSerializer(host).data
        if live.type == 'STREAM':
            data = {'host': data_host,
                    'users': data_user}
        elif live.type == 'CHAT':
            data = data_user
        else:
            data = {
                'host': data_host,
                'keys': data_key,
                'users': data_user
            }
        return data, "Danh sách người tham gia", status.HTTP_200_OK


class SearchLiveByKeywordAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        keyword = request.query_params.get('keyword', '')

        list_live = LiveStreamingHistory.objects.select_related('cover_image', 'host').annotate(
            unaccented_name=Unaccent(F('name')),
            unaccented_id_show=Unaccent(F('id_show'))
        ).filter(
            (
                    Q(unaccented_name__icontains=keyword) |
                    Q(unaccented_id_show__icontains=keyword)
            ) &
            Q(is_stopped=False, is_hide=False)
        ).order_by('-user_view').exclude(type='STREAM')

        serializer = LiveStreamingSerializer(list_live, many=True)
        return serializer.data, "Danh sách phòng live", status.HTTP_200_OK


class SearchLiveStreamByKeywordAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        keyword = request.query_params.get('keyword', '')

        list_live = LiveStreamingHistory.objects.select_related('cover_image', 'host').annotate(
            unaccented_name=Unaccent(F('name')),
            unaccented_id_show=Unaccent(F('id_show'))
        ).filter(
            (
                    Q(unaccented_name__icontains=keyword) |
                    Q(unaccented_id_show__icontains=keyword)
            ) &
            Q(is_stopped=False, is_hide=False),
            type='STREAM'
        ).order_by('-user_view')

        serializer = LiveStreamingSerializer(list_live, many=True)
        return serializer.data, "Danh sách phòng live", status.HTTP_200_OK


#   =========================  List Gift, Send Gift, Send Message ==========================
class GetListGiftChatAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        qs = Gift.objects.all().order_by('price')

        serializer = GiftSerializer(qs, many=True)
        return serializer.data, "Danh sách qùa tặng", status.HTTP_200_OK


class GetListEmojiChatAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        qs = Emoji.objects.only('id', 'image').all()

        serializer = EmojiSerializer(qs, many=True)
        return serializer.data, "Danh sách emoji", status.HTTP_200_OK


class SendGiftAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        qs = Gift.objects.all().order_by('amount')

        serializer = GiftSerializer(qs, many=True)
        return serializer.data, "Danh sách qùa tặng", status.HTTP_200_OK


class SendMessageToLiveAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        try:
            is_ban, banned_to = request.user.reportmessage.check_banned()
            if is_ban:
                return {}, f"Bạn đang bị cấm chat đến {banned_to}", status.HTTP_400_BAD_REQUEST
        except:
            ...

        live = LiveStreamingHistory.objects.defer('view').get(id=pk)
        msg_id = request.data.get('id')
        msg_type = request.data.get('type')
        sender = request.user
        text = request.data.get('text', None)
        # Tạo tin nhắn
        if msg_id:
            msg = MessageLive(type=msg_type,
                              id=uuid.UUID(msg_id),
                              text=text,
                              sender=sender,
                              live=live,
                              )
        else:
            msg = MessageLive(type=msg_type,
                              text=text,
                              sender=sender,
                              live=live,
                              )
        try:
            msg.full_clean()  # Kiểm tra và chạy các validators
            msg.save()  # Lưu đối tượng vào cơ sở dữ liệu
        except Exception as e:
            return str(e), "Tồn tại từ ngữ vi phạm qui tắc cộng đồng", status.HTTP_400_BAD_REQUEST

        files = request.data.get('file', None)
        if files:
            msg.file.set(files)
            msg.text = f"{msg.sender.full_name} đã chia sẻ {len(files)} file"
            msg.save()
        if msg_type == 'STICKER':
            msg.text = f"{sender.full_name} đã gửi một nhãn dán"
            msg.sticker = Sticker.objects.get(id=request.data.get('sticker_id'))
            msg.save()
        serializer_msg = MessageLiveSerializer(msg, context={'request': request})
        data_msg = serializer_msg.data

        send_new_message_to_live.s(str(live.id), str(msg.id)).apply_async(countdown=0)

        return data_msg, "Gửi tin nhắn thành công", status.HTTP_200_OK


class SendGiftToLiveAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        live = LiveStreamingHistory.objects.defer('view').get(id=pk)
        amount = request.data.get('amount')
        sender = request.user
        receivers = request.data.get('receiver_id')
        gift_send = Gift.objects.get(id=request.data.get('gift_id'))
        user_gift = UserGift.objects.get_or_create(gift=gift_send, user=request.user)[0]
        if user_gift.quantity < amount * len(receivers):
            quantity_need = amount - user_gift.quantity
            wallet = Wallet.objects.get_or_create(user=request.user)[0]
            if wallet.current_balance < gift_send.price * quantity_need:
                return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

            user_gift = UserGift.objects.get_or_create(user=request.user,
                                                       gift=gift_send)[0]
            user_gift.add_quantity(quantity_need)
            wallet.subtract_balance(gift_send.price * quantity_need)
            trans = Transaction.objects.create(from_user=request.user,
                                               funds='Coin',
                                               transaction_type='gift',
                                               amount=gift_send.price,
                                               return_code='00'
                                               )
            data_trade = GiftSerializer(gift_send).data
            trans.add_detail("gift", data_trade)

        gift = GiftLog.objects.create(gift=gift_send,
                                      sender=sender,
                                      amount=amount,
                                      live_streaming=live
                                      )
        msg = MessageLive(type='GIFT',
                          text=f"{sender.full_name} vừa tặng {gift.amount} {gift_send.title}",
                          sender=sender,
                          live=live,
                          )
        msg.save()  # Lưu đối tượng vào cơ sở dữ liệu
        send_new_message_to_live.s(str(live.id), str(msg.id)).apply_async(countdown=0)

        gift.receiver.set(receivers)
        gift.save()

        # Thêm task ngay đây
        for receiver in gift.receiver.all():
            UserGift.objects.get_or_create(gift=gift_send, user=receiver)[0].add_quantity(gift.amount)
            user_gift.sub_quantity(gift.amount)
            send_not_save_notification(user=receiver,
                                       title='Thông báo',
                                       body=f"{sender.full_name} vừa gửi cho bạn {amount} {gift.gift.title}")
        serializer_msg = GiftLogSerializer(gift, context={'request': request})
        data_msg = serializer_msg.data

        send_gift_to_live.s(str(gift.id)).apply_async(countdown=0)

        return data_msg, "Gửi quà thành công", status.HTTP_200_OK


class SendEmojiToLiveAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        live = LiveStreamingHistory.objects.defer('view').get(id=pk)

        sender = request.user

        emoji_send = Emoji.objects.get(id=request.data.get('emoji_id'))

        emoji = EmojiLog.objects.create(emoji=emoji_send,
                                        sender=sender,
                                        live=live
                                        )
        serializer_msg = EmojiLogSerializer(emoji, context={'request': request})
        data_msg = serializer_msg.data

        send_emoji_to_live.s(str(emoji.id)).apply_async(countdown=0)

        return data_msg, "Gửi emoji thành công", status.HTTP_200_OK


class HistoryMsgOfLiveAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request, pk):
        live = LiveStreamingHistory.objects.defer('view').get(id=pk)
        messages = MessageLive.objects.select_related('live', 'sender').prefetch_related('file').filter(
            live=live).order_by(
            '-created_at')

        qs, paginator = get_paginator_limit_offset(messages, request)
        serializer_data = MessageLiveSerializer(qs, many=True).data

        data = paginator.get_paginated_response(serializer_data).data

        return data, "Lịch sủ tin nhắn", status.HTTP_200_OK


class HistoryChairsOfLiveAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request, pk):
        live = LiveStreamingHistory.objects.defer('view').get(id=pk)
        live_users = LiveUser.objects.filter(live_streaming=live,
                                             is_live=True,
                                             is_online=True).order_by('updated_at')
        serializer = LiveUserSerializer(live_users, many=True)
        return serializer.data, "Danh sách người trên ghế", status.HTTP_200_OK


class DetailLiveAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request, pk):
        live = LiveStreamingHistory.objects.defer('view').get(id=pk)
        serializer = LiveStreamingSerializer(live)
        return serializer.data, "Chi tiết phòng", status.HTTP_200_OK


class OnOffMicroAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        is_on_mic = request.query_params.get('is_on', False)

        is_on = True if is_on_mic == 'true' else False
        live = LiveStreamingHistory.objects.defer('view').get(id=pk)
        live_user = LiveUser.objects.get(user=request.user,
                                         live_streaming=live)

        live_user.set_micro(is_on)
        if is_on:
            send_new_join_leave_to_live.s(live_id=str(live.id),
                                          live_user_id=str(live_user.id),
                                          event='NEW_ON_MIC').apply_async(countdown=0)
        else:
            send_new_join_leave_to_live.s(live_id=str(live.id),
                                          live_user_id=str(live_user.id),
                                          event='NEW_OFF_MIC').apply_async(countdown=0)
        return {}, "Bật/Tắt mic thành công", status.HTTP_200_OK
