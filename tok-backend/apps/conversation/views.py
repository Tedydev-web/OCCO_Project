import datetime
import json
import time
from itertools import chain

from django.db import transaction
from django.db.models import Q, Case, When, Value, IntegerField, Count, Prefetch
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.services.firebase import send_and_save_notification
from apps.conversation.models import Room, RandomQueue, RoomUser, Message, Call, PrivateQueue, PinnedMessage, \
    SeenByMessage
from apps.conversation.serializers import RoomSerializer, RoomDetailSerializer, MessageSerializer, UserBasicSerializer, \
    RoomSearchSerializer, ListRoomSerializer, LastMessageSerializer, RoomUserBasicSerializer, MessageCreateSerializer, \
    PinnedMessageSerializer, BackGroundColorSerializer, MessageIdSerializer
from apps.conversation.task import send_message_to_socket_users_in_room, send_event_to_socket_users_in_room, \
    send_group_to_socket_users_in_room, send_new_message_to_room, update_seen_message, chk_and_update_seen_message
from apps.general.models import DevSetting, Report, FileUpload, BackGroundColor
from apps.user.models import CustomUser, FriendShip
from ultis.api_helper import api_decorator
from ultis.helper import get_paginator_data, get_paginator_limit_offset
from ultis.socket_helper import get_socket_data, send_to_socket, send_noti_to_socket_user, get_socket_data_conversation


class GetListOnlineUsersAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        user = request.user
        room = Room.objects.filter(roomuser__user=user, type='CONNECT', newest_at__isnull=False)
        if room:
            user_room_id = RoomUser.objects.filter(room__in=room,
                                                   user__is_online=True).select_related('user').exclude(
                user=user).values_list(
                'user',
                flat=True)[:20]
        else:
            user_room_id = []

        users_id = list(set(chain(user_room_id, list(user.social.get('friends', [])))))

        qs = CustomUser.objects.select_related('avatar').filter(id__in=users_id, is_online=True).distinct()[:20]

        serializer = UserBasicSerializer(qs, many=True, context={'request': request})
        return serializer.data, "Danh sách người dùng online", status.HTTP_200_OK


class GetListMessageOfRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        qs = Message.objects.prefetch_related('deleted_by',
                                              'file', 'seenbymessage_set').select_related('room', 'sender',
                                                                                          'reply_to').filter(
            room__id=pk).exclude(
            deleted_by=request.user).order_by('-created_at')
        # chk_and_update_seen_message.s(str(request.user.id), str(pk)).apply_async(countdown=0)
        qs, paginator = get_paginator_limit_offset(qs, request)

        room_user = RoomUser.objects.get(room__id=pk, user=request.user)
        room_user.reset_total_unseen()

        serializer = MessageSerializer(qs, many=True, context={'request': request})
        paginator_data = paginator.get_paginated_response(serializer.data).data
        return paginator_data, "Danh sách tin nhắn", status.HTTP_200_OK


class GetListMessageUnseenOfRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        qs = Message.objects.prefetch_related('deleted_by',
                                              'file').select_related('room', 'sender').filter(room__id=pk,
                                                                                              created_at__gte=datetime.datetime.now()).order_by(
            '-created_at')
        qs, paginator = get_paginator_limit_offset(qs, request)

        serializer = MessageSerializer(qs, many=True, context={'request': request})
        paginator_data = paginator.get_paginated_response(serializer.data).data
        return paginator_data, "Danh sách tin nhắn", status.HTTP_200_OK


class CreateRoomOfUserToUseAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        receiver = CustomUser.objects.get(id=pk)
        sender = request.user

        room = Room.objects.filter(
            Q(roomuser__user=receiver) &
            Q(type='CONNECT')).filter(
            Q(roomuser__user=sender)
        ).first()

        if not room:
            room = Room.objects.create(type='CONNECT')
            room_users = RoomUser.objects.bulk_create([
                RoomUser(room=room, user=sender),
                RoomUser(room=room, user=receiver)
            ])

        serializer = RoomSerializer(room, context={'request': request})
        return serializer.data, "Tạo phòng thành công", status.HTTP_200_OK


class GetListRoomChatOfUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        type_room = request.query_params.get('type', 'CONNECT')
        room_id = RoomUser.objects.select_related('room', 'user').filter(user=request.user,
                                                                         date_removed__isnull=True
                                                                         ).values_list('room', flat=True)
        qs = Room.objects.prefetch_related(
            Prefetch('roomuser_set', queryset=RoomUser.objects.select_related('user'), to_attr='room_users')
        ).filter(
            id__in=room_id,
            newest_at__isnull=False
        ).annotate(
            user_count=Count('roomuser')
        ).filter(
            user_count__gt=1  # Only include rooms with more than one user
        ).order_by('-newest_at')
        if type_room == 'CONNECT':
            qs = qs.filter(type__in=[type_room, 'PRIVATE', 'CSKH'])
        else:
            qs = qs.filter(type='GROUP')
        data, paginator = get_paginator_limit_offset(qs, request)
        serializer = ListRoomSerializer(data, many=True, context={'request': request})
        data_lm = paginator.get_paginated_response(serializer.data).data
        return data_lm, "Danh sách room", status.HTTP_200_OK


class DetailRoomChatOfUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        room = Room.objects.prefetch_related(
            Prefetch('roomuser_set', queryset=RoomUser.objects.select_related('user')),
            Prefetch('message_set',
                     queryset=Message.objects.prefetch_related('deleted_by',
                                                               'file').select_related('room', 'sender'))).get(id=pk)
        rs = RoomUser.objects.get(room=room,
                                  user=request.user)
        rs.set_active()
        rs.reset_total_unseen()

        # serializer = RoomSerializer(room, context={'request': request})
        return {}, "", status.HTTP_200_OK


#   =========================  Chat  ==========================
class SendMessageToRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        # Check banned
        try:
            is_ban, banned_to = request.user.reportmessage.check_banned()
            if is_ban:
                return {}, f"Bạn đang bị cấm chat đến {banned_to}", status.HTTP_400_BAD_REQUEST
        except:
            ...
        try:
            with transaction.atomic():
                room = Room.objects.prefetch_related('roomuser_set').get(id=pk)
                users = room.roomuser_set.all()

                if room.type == 'PRIVATE' and users.filter(block_status_private__isnull=True).count() != 2:
                    return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST
                else:
                    if users.count() == 2:
                        if CustomUser.custom_objects.is_block(request.user,
                                                              users.exclude(
                                                                  user=request.user).first().user) is not None:
                            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

                serializer = MessageCreateSerializer(data=request.data, context={'request': request, 'room': room})

                if not serializer.is_valid():
                    return str(
                        serializer.errors), "Tồn tại từ ngữ vi phạm qui tắc cộng đồng", status.HTTP_400_BAD_REQUEST

                msg = serializer.save()
                serializer_msg = MessageSerializer(msg, context={'request': request})
                data_msg = serializer_msg.data

                send_new_message_to_room.s(str(room.id), str(msg.id), str(request.user.id)).apply_async(countdown=0)

                return data_msg, "Gửi tin nhắn thành công", status.HTTP_200_OK
        except Exception as e:
            return {str(e)}, "Có lỗi xảy ra khi gửi tin nhắn", status.HTTP_400_BAD_REQUEST


class MarkUnSeenAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        sender = request.user

        room_user = RoomUser.objects.filter(room=room, user=sender).first()
        room_user.set_total_unseen()

        return {}, "Đánh dấu chưa đọc thành công", status.HTTP_200_OK


class ListPinMsgOfRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        qs = PinnedMessage.objects.filter(room=room).order_by('-created_at')
        serializer = PinnedMessageSerializer(qs, many=True, context={'request': request})

        return serializer.data, "Danh sách pinned msg", status.HTTP_200_OK


#   =========================  Call  ==========================
class CallToRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        room.set_newest()

        sender = request.user

        # Tạo tin nhắn
        call = Call.objects.create(type='CALL',
                                   status='WAITING')

        msg = Message.objects.create(type='CALL',
                                     sender=sender,
                                     room=room,
                                     call=call)

        serializer_msg = MessageSerializer(msg, context={'request': request})
        serializer_room = RoomSerializer(room, context={'request': request})

        data_msg = serializer_msg.data

        send_to_socket('conversation', str(room.id), get_socket_data('NEW_CALL', data_msg))
        rs = room.roomuser_set.all()
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_CALL', data_msg,
                                                        room_id=str(room.id)))

        return data_msg, "Gọi thành công", status.HTTP_200_OK


class UserHandleCallAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        #
        type_call = request.data.get('type_call')
        type_handle = request.data.get('type_handle')
        msg = Message.objects.get(id=pk)
        call = msg.call
        if type_handle == 'ACCEPTED':
            call.set_status(type_handle)
            call.start_call()
        elif type_handle == 'CANCELED':
            call.set_status(type_handle)
        elif type_handle == 'REJECTED':
            call.set_status(type_handle)
        else:
            call.end_call()
            call.set_type(type_call)
            call.set_status(type_handle)

        serializer = MessageSerializer(msg, context={'request': request})
        data_msg = serializer.data
        #
        rs = msg.room.roomuser_set.select_related('user').all()
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_CALL', data_msg,
                                                        room_id=str(msg.room.id)))
        #
        return data_msg, f"{type_call} {type_handle} Thành công", status.HTTP_200_OK
    #   =========================  Remove, revoke  ==========================


class UserRemoveRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        user = request.user
        rs = RoomUser.objects.get(room__id=pk,
                                  user=user)
        rs.date_removed = timezone.now()
        rs.last_message = {}
        rs.is_removed = True
        rs.reset_total_unseen()
        rs.save()
        messages = Message.objects.select_related('room').filter(room__id=pk)

        # Sử dụng transaction để đảm bảo tính toàn vẹn của dữ liệu
        with transaction.atomic():
            # Lặp qua danh sách tin nhắn và thêm user vào deleted_by
            for message in messages:
                message.deleted_by.add(user)
                message.save()

        return {}, "Xoá phòng thành công", status.HTTP_200_OK


class UserRemoveMessageAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        msg = Message.objects.get(id=request.data.get('msg_id'))
        room_user = RoomUser.objects.get(room=msg.room, user=request.user)

        qs = Message.objects.filter(room=msg.room, reply_to=msg).only('id')
        qs = MessageIdSerializer(qs, many=True).data
        data = MessageSerializer(msg, context={'request': request}).data
        data = {
            'msg': data,
            'list_id': qs
        }
        rs = msg.room.roomuser_set.select_related('user').all()
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_REMOVE_MSG', data,
                                                        room_id=str(msg.room.id)))

        if request.data.get('is_all'):
            msg.delete()
            # Xoá tin nhắn cuối 2 phía
            if str(msg.id) == room_user.last_message['id']:
                msg.delete()
                last_message = msg.room.message_set.order_by('-created_at').first()
                serializer = LastMessageSerializer(last_message, context={'request': request})
                last_message = serializer.data
                for rs in msg.room.roomuser_set.all():
                    rs.set_last_message(last_message)

        else:
            msg.deleted_by.add(request.user)
            msg.save()
            # Xoá tin nhắn cuối 1 phía
            if str(msg.id) == room_user.last_message['id']:
                last_message = msg.room.message_set.order_by('-created_at').exclude(deleted_by=request.user).first()
                serializer = LastMessageSerializer(last_message, context={'request': request})
                last_message = serializer.data
                room_user.set_last_message(last_message)

        return {}, "Xoá tin nhắn thành công", status.HTTP_200_OK


class UserRevokeMessageAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        msg = Message.objects.get(id=pk)

        msg.is_revoked = True
        msg.save()
        data = MessageSerializer(msg, context={'request': request}).data
        qs = Message.objects.filter(room=msg.room, reply_to=msg).only('id')
        qs = MessageIdSerializer(qs, many=True).data
        data = {
            'msg': data,
            'list_id': qs
        }
        rs = msg.room.roomuser_set.select_related('user').all()
        for r in rs:
            if str(msg.id) == r.last_message['id']:
                r.last_message['text'] = 'Tin nhắn đã bị thu hồi'
                r.save()

            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_REVOKE_MSG', data,
                                                        room_id=str(msg.room.id)))

        return {}, "Thu hồi tin nhắn thành công", status.HTTP_200_OK


class UserEditMessageAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        msg = Message.objects.get(id=pk)
        edit_text = request.query_params.get('edit_text')

        room = Room.objects.prefetch_related('roomuser_set').get(id=msg.room.id)
        users = room.roomuser_set.all()
        if users.count() == 2:
            if CustomUser.custom_objects.is_block(request.user,
                                                  users.exclude(user=request.user).first().user) is not None:
                return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        msg.text = edit_text
        room_user = RoomUser.objects.get(room=msg.room, user=request.user)
        msg.is_edited = True
        msg.save()
        if str(msg.id) == room_user.last_message['id']:
            last_message = msg.room.message_set.order_by('-created_at').first()
            serializer = LastMessageSerializer(last_message, context={'request': request})
            last_message = serializer.data
            for rs in msg.room.roomuser_set.all():
                rs.set_last_message(last_message)

        data = MessageSerializer(msg, context={'request': request}).data
        rs = msg.room.roomuser_set.select_related('user').all()
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_EDIT_MSG', data,
                                                        room_id=str(msg.room.id)))

        return {}, "Chỉnh sửa tin nhắn thành công", status.HTTP_200_OK


class UserPinMessageAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        msg = Message.objects.get(id=pk)
        pinned = PinnedMessage.objects.create(message=msg,
                                              pinner=request.user,
                                              room=msg.room)
        msg.is_pinned = True
        msg.save()

        data = MessageSerializer(msg, context={'request': request}).data
        rs = msg.room.roomuser_set.select_related('user').all()
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_PIN_MSG', data,
                                                        room_id=str(msg.room.id)))
        data_pinned = PinnedMessageSerializer(pinned).data
        return data_pinned, "Ghim tin nhắn thành công", status.HTTP_200_OK


class UserUnPinMessageAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        msg = Message.objects.get(id=pk)
        pinned = PinnedMessage.objects.filter(message=msg)
        pinned.delete()

        msg.is_pinned = False
        msg.save()

        data = MessageSerializer(msg, context={'request': request}).data
        rs = msg.room.roomuser_set.select_related('user').all()
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_UNPIN_MSG', data,
                                                        room_id=str(msg.room.id)))
        return {}, "Bỏ Ghim tin nhắn thành công", status.HTTP_200_OK


class UserUpdateSeenMessageAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        update_seen_message.s(str(request.user.id), str(pk)).apply_async(countdown=0)

        return {}, "Đọc tin nhắn thành công", status.HTTP_200_OK


#   =========================  Join Random, Private  ==========================
class JoinRandomChatAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        start_time = time.time()
        while True:
            user = request.user
            # Set cache here
            recommended_users = CustomUser.custom_objects.recommend_users(user).values_list('id', flat=True)
            if DevSetting.get_value('random_filter') == 'true' or DevSetting.get_value('random_filter'):
                is_random_filter = True
            else:
                is_random_filter = False

            # Check if user in a random room
            room = Room.objects.filter(type='RANDOM', roomuser__user=user,
                                       is_used=False).first()
            if room:
                room.set_used()  # Update room random is_used = True
                room.set_connect()
                serializer = RoomSerializer(room, context={'request': request})
                return serializer.data, "Tìm thấy người tham gia và tạo phòng", status.HTTP_200_OK

            # Join to queue here
            user_join = RandomQueue.objects.get_or_create(user=user)[0]

            if user_join.is_stop:
                user_join.delete()
                return {}, "Đã huỷ yêu cầu tìm phòng", status.HTTP_204_NO_CONTENT

            # Finding other in queue
            if not is_random_filter:
                # Exclude block and user
                blocked = CustomUser.custom_objects.list_block(user)
                other = RandomQueue.objects.exclude(user__in=blocked | CustomUser.objects.filter(id=user.id)).first()
            else:
                # Filter recommend
                other = RandomQueue.objects.filter(user__id__in=recommended_users).first()
            # If other exist, create room and delete in queue
            if other:
                # Check if exists room
                if not Room.objects.filter(Q(type='CONNECT') & Q(roomuser__user=user)).filter(
                        Q(roomuser__user=other.user)).first():
                    user_join.delete()
                    room = Room.objects.create(type='RANDOM')
                    RoomUser.objects.bulk_create([
                        RoomUser(room=room, user=user),
                        RoomUser(room=room, user=other.user)
                    ])
                    serializer = RoomSerializer(room, context={'request': request})
                    other.delete()
                    return serializer.data, "Tìm thấy người tham gia và tạo phòng", status.HTTP_200_OK

            # Check if
            if time.time() - start_time > DevSetting.get_time_queue():
                user_join.delete()
                return {}, "Không tìm thấy người dùng", status.HTTP_204_NO_CONTENT

            time.sleep(1)


class JoinPrivateChatAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        start_time = time.time()
        while True:
            user = request.user
            # Check if user in a random room
            room = Room.objects.filter(type='PRIVATE', roomuser__user=user,
                                       is_used=False).first()
            if room:
                room.set_used()  # Update room random is_used = True
                serializer = RoomSerializer(room, context={'request': request})
                return serializer.data, "Tìm thấy người tham gia và tạo phòng", status.HTTP_200_OK

            # Join to queue here
            user_join, created = PrivateQueue.objects.get_or_create(user=user)

            if user_join.is_stop:
                user_join.delete()
                return {}, "Đã huỷ yêu cầu tìm phòng", status.HTTP_204_NO_CONTENT

            # Finding other in queue
            other = PrivateQueue.objects.exclude(user=user).first()
            # If other exist, create room and delete in queue
            if other:
                user_join.delete()
                room = Room.objects.create(type='PRIVATE')
                RoomUser.objects.bulk_create([
                    RoomUser(room=room, user=user),
                    RoomUser(room=room, user=other.user)
                ])
                other.delete()
                serializer = RoomSerializer(room, context={'request': request})
                return serializer.data, "Tìm thấy người tham gia và tạo phòng", status.HTTP_200_OK

            # Check if
            if time.time() - start_time > DevSetting.get_time_queue():
                user_join.delete()
                return {}, "Không tìm thấy người dùng", status.HTTP_204_NO_CONTENT

            time.sleep(1)


#   =========================  Leave , Accept Queue Room   ==========================
class LeaveRandomRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        serializer = RoomSerializer(room, context={'request': request})

        room.set_leaved()
        data = serializer.data
        other = room.roomuser_set.select_related('user').all().exclude(user=request.user).first()

        send_to_socket('conversation', str(other.user.id), get_socket_data_conversation('CLOSE_RANDOM', data,
                                                                                        room_id=str(room.id)))

        return serializer.data, "Đã rời khỏi chat ngẫu nhiên", status.HTTP_200_OK


class LeavePrivateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        serializer = RoomDetailSerializer(room, context={'request': request})
        data_room = serializer.data
        other = room.roomuser_set.select_related('user').all().exclude(user=request.user).first()
        send_to_socket('conversation', str(other.user.id),
                       get_socket_data_conversation('CLOSE_PRIVATE', data_room,
                                                    room_id=str(room.id)))

        return data_room, "Đã rời khỏi chat ẩn danh", status.HTTP_200_OK


class StopQueueAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        PrivateQueue.objects.select_related('user').filter(user=request.user).update(is_stop=True)
        RandomQueue.objects.select_related('user').filter(user=request.user).update(is_stop=True)

        return {}, "Dừng tìm thành công", status.HTTP_200_OK
    #   =========================  Seen, Remove, Block, Report  ==========================


class ReasonAPIView(APIView):

    @api_decorator
    def get(self, request):
        file_path = 'constants/report.json'
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data, 'Lý do tố cáo!', status.HTTP_200_OK


class SearchUserConversationAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        keyword = request.query_params.get('keyword')
        user = request.user

        room = Room.objects.filter(roomuser__user=user, type='CONNECT')

        user_room = []
        if room:
            user_room = RoomUser.objects.filter(room__in=room,
                                                user__full_name__icontains=keyword).select_related('user').exclude(
                user__id=request.user.id)[:20].values_list(
                'user',
                flat=True)

        friend_s = CustomUser.custom_objects.list_friend(user).filter(full_name__icontains=keyword)

        users = list(set(chain(CustomUser.objects.filter(id__in=user_room).select_related('avatar'), friend_s)))

        qs, paginator = get_paginator_limit_offset(users, request)

        serializer_user = UserBasicSerializer(qs, many=True)

        data = paginator.get_paginated_response(serializer_user.data).data

        return data, 'Danh sách tìm kiếm!', status.HTTP_200_OK


class SearchRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        keyword = request.query_params.get('keyword')
        user = request.user

        room_s = Room.objects.filter(
            Q(roomuser__user=user) &
            (
                    Q(roomuser__user__full_name__icontains=keyword) |
                    Q(name__icontains=keyword)
            ) &
            Q(type='GROUP')
        )

        qs, paginator = get_paginator_limit_offset(room_s, request)

        serializer_room = RoomSearchSerializer(room_s, many=True)

        data = paginator.get_paginated_response(serializer_room.data).data

        return data, 'Danh sách tìm kiếm!', status.HTTP_200_OK


class SearchConversationRecommendAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        user = request.user

        room = Room.objects.filter(roomuser__user=user, type='CONNECT')

        user_room = []
        if room:
            user_room = RoomUser.objects.filter(room__in=room).select_related('user').exclude(
                user__id=user.id)[:20].values_list(
                'user',
                flat=True)

        users_recommend = CustomUser.objects.filter(id__in=user_room).select_related('avatar').prefetch_related(
            'groups', 'user_permissions')
        serializer_recommend = UserBasicSerializer(users_recommend, many=True)

        return serializer_recommend.data, 'Danh sách gợi ý!', status.HTTP_200_OK

    class SearchConversationRecommendAPIView(APIView):
        permission_classes = [IsAuthenticated, ]

        @api_decorator
        def get(self, request):
            user = request.user

            room = Room.objects.filter(roomuser__user=user, type='CONNECT')

            user_room = []
            if room:
                user_room = RoomUser.objects.filter(room__in=room).select_related('user').exclude(
                    user__id=user.id)[:20].values_list(
                    'user',
                    flat=True)

            users_recommend = CustomUser.objects.filter(id__in=user_room).select_related('avatar').prefetch_related(
                'groups', 'user_permissions')
            serializer_recommend = UserBasicSerializer(users_recommend, many=True)

            return serializer_recommend.data, 'Danh sách gợi ý!', status.HTTP_200_OK


class SearchMessageInRoomAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        room_id = request.query_params.get('room_id', None)
        keyword = request.query_params.get('keyword', '')
        qs = Message.objects.prefetch_related('deleted_by',
                                              'file', 'seenbymessage_set').select_related('room', 'sender',
                                                                                          'reply_to').filter(
            room__id=room_id,
            text__unaccent__icontains=keyword).exclude(
            deleted_by=request.user).order_by('-created_at')
        qs, paginator = get_paginator_limit_offset(qs, request)
        serializer_message = MessageSerializer(qs, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer_message.data).data
        return data, 'Danh sách tin nhắn!', status.HTTP_200_OK
    #   =========================  Group  ==========================


class CreateUpdateGroupAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        if len(request.data.get('users_id', [])) < 2:
            return {}, "Vui lòng chọn từ 2 thành viên trở lên", status.HTTP_400_BAD_REQUEST

        image = FileUpload.objects.get(id=request.data.get('image'))
        room = Room.objects.create(name=request.data.get('name'), type='GROUP', image=image)
        users = CustomUser.objects.filter(id__in=request.data.get('users_id'))
        Message.objects.create(type='HISTORY', text=f'{request.user.full_name} đã tạo nhóm', sender=request.user,
                               room=room)

        # ít nhất 2 thành viên, client chặn
        for user in users:
            RoomUser.objects.create(room=room,
                                    user=user, role='USER')
            Message.objects.create(type='HISTORY',
                                   text=f'{request.user.full_name} đã thêm {user.full_name} vào nhóm',
                                   sender=request.user,
                                   room=room)

        # chủ nhóm
        RoomUser.objects.create(room=room, user=request.user, role='HOST')
        room.set_newest()

        serializer = RoomSerializer(room, context={'request': request})
        data_room = serializer.data

        send_group_to_socket_users_in_room.s(room_id=str(room.id),
                                             event='NEW_GROUP_CREATE',
                                             user_id=str(request.user.id)).apply_async(countdown=0)

        return data_room, "Tạo nhóm thành công!", status.HTTP_200_OK

    @api_decorator
    def put(self, request, pk):
        room = Room.objects.get(id=pk)

        serializer = RoomSerializer(room, data=request.data, partial=True, context={'request': request})
        list_msg = []

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            if request.data.get('name'):
                msg_name = Message.objects.create(type='HISTORY',
                                                  text=f'{request.user.full_name} đã thay đổi tên nhóm!',
                                                  sender=request.user,
                                                  room=room)
                list_msg.append(str(msg_name.id))

            if request.data.get('image'):
                msg_image = Message.objects.create(type='HISTORY',
                                                   text=f'{request.user.full_name} đã thay đổi ảnh nhóm!',
                                                   sender=request.user,
                                                   room=room)
                list_msg.append(str(msg_image.id))

        send_group_to_socket_users_in_room.s(room_id=str(room.id),
                                             event='NEW_GROUP_UPDATE',
                                             user_id=str(request.user.id)).apply_async(countdown=0)

        send_message_to_socket_users_in_room.s(room_id=str(room.id),
                                               list_msg=list_msg).apply_async(countdown=0)

        return {}, "Cập nhật thành công!", status.HTTP_200_OK


class ChooseHostToLeaveAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_new_host = CustomUser.objects.get(id=request.data.get('user_id'))
        room = Room.objects.get(id=request.data.get('room_id'))
        room_user = RoomUser.objects.get(room=room, user=request.user)
        if room_user.role == 'HOST':

            new_host = RoomUser.objects.get(user=user_new_host, room=room)
            new_host.set_new_role('HOST')

            room_user.delete()
            list_msg = []
            msg1 = Message.objects.create(type='HISTORY',
                                          text=f'{request.user.full_name} đã chỉ định {user_new_host.full_name} làm trưởng nhóm',
                                          sender=request.user,
                                          room=room)

            msg2 = Message.objects.create(type='HISTORY',
                                          text=f'{request.user.full_name} đã rời khỏi nhóm',
                                          sender=request.user,
                                          room=room)
            list_msg.append(str(msg1.id))
            list_msg.append(str(msg2.id))

            send_event_to_socket_users_in_room.s(room_id=str(room.id),
                                                 event='NEW_HOST_LEAVE').apply_async(countdown=0)

            send_message_to_socket_users_in_room.s(room_id=str(room.id),
                                                   list_msg=list_msg).apply_async(countdown=0)

            return {}, 'Thay đổi trưởng nhóm và rời nhóm thành công!', status.HTTP_200_OK
        else:
            return {}, 'Không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class ChooseNewHostAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_new_host = CustomUser.objects.get(id=request.data.get('user_id'))
        room = Room.objects.get(id=request.data.get('room_id'))
        room_user = RoomUser.objects.get(room=room, user=request.user)
        if room_user.role == 'HOST':

            new_host = RoomUser.objects.get(user=user_new_host, room=room)
            new_host.set_new_role('HOST')

            room_user.set_new_role('USER')
            list_msg = []
            msg = Message.objects.create(type='HISTORY',
                                         text=f'{request.user.full_name} đã chỉ định {user_new_host.full_name} làm trưởng nhóm',
                                         sender=request.user,
                                         room=room)

            list_msg.append(str(msg.id))
            send_event_to_socket_users_in_room.s(room_id=str(room.id),
                                                 event='NEW_HOST_CHANGE').apply_async(countdown=0)

            send_message_to_socket_users_in_room.s(room_id=str(room.id),
                                                   list_msg=list_msg).apply_async(countdown=0)

            return {}, 'Thay đổi trưởng nhóm thành công!', status.HTTP_200_OK
        else:
            return {}, 'Không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class ChooseMemberToKeyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_new_key = CustomUser.objects.get(id=request.data.get('user_id'))

        room = Room.objects.get(id=request.data.get('room_id'))

        check_room_host = RoomUser.objects.filter(room=room, user=request.user, role='HOST').exists()
        check_room_key = RoomUser.objects.filter(room=room, role='KEY').count()
        if check_room_host:
            if check_room_key < 3:
                room_user = RoomUser.objects.get(room=room, user=user_new_key)
                room_user.set_new_role('KEY')
                list_msg = []
                msg = Message.objects.create(type='HISTORY',
                                             text=f'{request.user.full_name} đã bổ nhiệm {user_new_key.full_name} làm phó nhóm',
                                             sender=request.user,
                                             room=room)
                list_msg.append(str(msg.id))
                send_event_to_socket_users_in_room.s(room_id=str(room.id),
                                                     event='NEW_KEY_ADD').apply_async(countdown=0)

                send_message_to_socket_users_in_room.s(room_id=str(room.id),
                                                       list_msg=list_msg).apply_async(countdown=0)

                return {}, 'Thêm phó nhóm thành công!', status.HTTP_200_OK
            else:
                return {}, 'Mỗi nhóm chỉ được tối đa 3 phó nhóm!', status.HTTP_400_BAD_REQUEST

        else:
            return {}, 'Bạn không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class RemoveMemberFromKeyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_new_key = CustomUser.objects.get(id=request.data.get('user_id'))

        room = Room.objects.get(id=request.data.get('room_id'))

        check_room_host = RoomUser.objects.filter(room=room, user=request.user, role='HOST').exists()
        if check_room_host:
            room_user = RoomUser.objects.get(room=room, user=user_new_key)
            room_user.set_new_role('USER')
            list_msg = []
            msg = Message.objects.create(type='HISTORY',
                                         text=f'{request.user.full_name} đã huỷ bỏ tư cách phó nhóm của {user_new_key.full_name}',
                                         sender=request.user,
                                         room=room)

            list_msg.append(str(msg.id))
            send_event_to_socket_users_in_room.s(room_id=str(room.id),
                                                 event='NEW_KEY_REMOVE').apply_async(countdown=0)

            send_message_to_socket_users_in_room.s(room_id=str(room.id),
                                                   list_msg=list_msg).apply_async(countdown=0)

            return {}, 'Bỏ tư cách thành công!', status.HTTP_200_OK

        else:
            return {}, 'Bạn không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class RemoveMemberAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        remove_user = CustomUser.objects.get(id=request.data.get('user_id'))

        room = Room.objects.get(id=request.data.get('room_id'))

        user = RoomUser.objects.get(room=room, user=request.user)

        if user.role == 'HOST':
            room_user_remove = RoomUser.objects.get(room=room, user=remove_user)
            list_msg = []

            msg = Message.objects.create(type='HISTORY',
                                         text=f'{request.user.full_name} đã xóa {remove_user.full_name} ra khỏi nhóm',
                                         sender=request.user,
                                         room=room)
            list_msg.append(str(msg.id))

            room_user_remove.delete()

            send_event_to_socket_users_in_room.s(room_id=str(room.id),
                                                 event='NEW_MEMBER_REMOVE').apply_async(countdown=0)

            send_message_to_socket_users_in_room.s(room_id=str(room.id),
                                                   list_msg=list_msg).apply_async(countdown=0)

            return {}, 'Xóa thành viên thành công!', status.HTTP_200_OK

        elif user.role == 'KEY':
            room_user_remove = RoomUser.objects.get(room=room, user=remove_user)
            list_msg = []
            if room_user_remove.role == 'USER':

                msg = Message.objects.create(type='HISTORY',
                                             text=f'{request.user.full_name} đã xóa {remove_user.full_name} ra khỏi nhóm',
                                             sender=request.user,
                                             room=room)
                list_msg.append(str(msg.id))
                room_user_remove.delete()

                send_event_to_socket_users_in_room.s(room_id=str(room.id),
                                                     event='NEW_MEMBER_REMOVE').apply_async(countdown=0)

                send_message_to_socket_users_in_room.s(room_id=str(room.id),
                                                       list_msg=list_msg).apply_async(countdown=0)

                return {}, 'Xóa thành viên thành công!', status.HTTP_200_OK
            else:
                return {}, 'Bạn không có quyền!', status.HTTP_400_BAD_REQUEST
        else:
            return {}, 'Chỉ trưởng nhóm hoặc phó nhóm có quyền này!', status.HTTP_200_OK


class RemoveGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        room = Room.objects.get(id=pk)
        room_user = RoomUser.objects.get(user=request.user, room=room)
        if room_user.role == 'HOST':
            send_group_to_socket_users_in_room.s(room_id=str(room.id),
                                                 event='NEW_GROUP_REMOVE',
                                                 user_id=str(request.user.id)).apply_async(countdown=0)
            room.delete()
            return {}, 'Xóa nhóm thành công!', status.HTTP_204_NO_CONTENT
        else:
            return {}, 'Bạn không phải trưởng nhóm!', status.HTTP_400_BAD_REQUEST


class ListUserInRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        room = Room.objects.get(id=pk)
        room_user = RoomUser.objects.filter(room=room).order_by('created_at')
        serializer = RoomUserBasicSerializer(room_user, many=True, context={'request': request})
        return serializer.data, "Danh sách user trong phòng", status.HTTP_200_OK


class AddMemberToGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        room = Room.objects.get(id=request.data.get('room_id'))

        users = CustomUser.objects.filter(id__in=request.data.get('users_id'))
        list_msg = []
        for user in users:
            room_user, created = RoomUser.objects.get_or_create(room=room, user=user)
            if created:
                room_user.set_new_role('USER')
            msg = Message.objects.create(type='HISTORY',
                                         text=f'{request.user.full_name} đã thêm {user.full_name} vào nhóm',
                                         sender=request.user,
                                         room=room)
            list_msg.append(str(msg.id))
        data_room = RoomSerializer(room, context={'request': request}).data

        send_group_to_socket_users_in_room.s(room_id=str(room.id),
                                             event='NEW_GROUP_CREATE',
                                             user_id=str(request.user.id)).apply_async(countdown=0)

        send_event_to_socket_users_in_room.s(room_id=str(room.id),
                                             event='NEW_MEMBER_ADD').apply_async(countdown=0)

        send_message_to_socket_users_in_room.s(room_id=str(room.id),
                                               list_msg=list_msg).apply_async(countdown=0)

        return data_room, 'Thêm thành viên thành công!', status.HTTP_200_OK


class LeaveGroupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        room_id = request.data.get('room_id')
        room = Room.objects.get(id=request.data.get('room_id'))

        try:
            room_user = RoomUser.objects.get(room_id=room_id, user=request.user)
            if room_user.role == 'HOST':
                return {}, 'Bạn là trưởng nhóm!', status.HTTP_400_BAD_REQUEST
            else:
                room_user.delete()

                # room_users = RoomUser.objects.filter(room__id=room_id)
                # serializer = RoomUserBasicSerializer(room_users, many=True)
                # data_room = serializer.data
                msg = Message.objects.create(type='HISTORY',
                                             text=f'{request.user.full_name} đã rời khỏi nhóm',
                                             sender=request.user,
                                             room=room)
                # data_msg = MessageSerializer(msg).data

                # for roomuser in room_users:
                #     send_to_socket('conversation', str(roomuser.user.id),
                #                    get_socket_data_conversation('NEW_MEMBER_LEAVE', data_room, room_id=str(room_id)))
                #     send_to_socket('conversation', str(roomuser.user.id),
                #                    get_socket_data_conversation('NEW_MESSAGE', data_msg, room_id=str(room.id)))
                send_event_to_socket_users_in_room.s(room_id=room_id,
                                                     event='NEW_MEMBER_LEAVE').apply_async(countdown=0)
                send_message_to_socket_users_in_room.s(room_id=room_id,
                                                       list_msg=[str(msg.id)]
                                                       ).apply_async(countdown=0)
                return {}, 'Đã rời nhóm!', status.HTTP_204_NO_CONTENT
        except:
            return {}, 'Chưa vào nhóm chat này!', status.HTTP_400_BAD_REQUEST

    #   =========================  Recall Msg  ==========================


class ListBackGroundColorAPIView(APIView):
    @api_decorator
    def get(self, request):
        qs = BackGroundColor.objects.filter(is_active=True)
        serializer = BackGroundColorSerializer(qs, many=True)
        return serializer.data, "Danh sách mã màu", status.HTTP_200_OK


class UpdateBackGroundAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        color = request.query_params.get('color_id', '')
        image = request.query_params.get('image_id', '')
        room = Room.objects.get(id=pk)
        if color != '':
            room.background_color = BackGroundColor.objects.get(id=color)
            room.background_image = None
        else:
            room.background_image = FileUpload.objects.get(id=image)
            room.background_color = None

        room.save()
        rs = room.roomuser_set.select_related('user').all()
        data = ListRoomSerializer(room, context={'request': request}).data
        for r in rs:
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_UPDATE_BACKGROUND', data,
                                                        room_id=str(room.id)))

        return data, "Cập nhật background thành công", status.HTTP_200_OK


class BlockRoom2UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        rs = room.roomuser_set.select_related('user').all()
        for r in rs:
            if r.block_status_private is not None:
                return {}, "Bạn đã bị chặn", status.HTTP_400_BAD_REQUEST

            if r.user == request.user:
                r.block_status_private = 'BLOCK'
                r.save()
                data_sender = ListRoomSerializer(room, context={'request': request}).data
                send_to_socket('conversation', str(r.user.id),
                               get_socket_data_conversation('NEW_BLOCK_PRIVATE', data_sender,
                                                            room_id=str(room.id)))
            else:
                r.block_status_private = 'BLOCKED'
                r.save()
                data_receiver = ListRoomSerializer(room, context={'request': request}).data
                send_to_socket('conversation', str(r.user.id),
                               get_socket_data_conversation('NEW_BLOCK_PRIVATE', data_receiver,
                                                            room_id=str(room.id)))

        return data_sender, "Chặn thành công", status.HTTP_200_OK


class UnBlockRoom2UserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        room = Room.objects.get(id=pk)
        rs = room.roomuser_set.select_related('user').all()
        for r in rs:
            r.block_status_private = None
            r.save()
            data = ListRoomSerializer(room, context={'request': request}).data
            send_to_socket('conversation', str(r.user.id),
                           get_socket_data_conversation('NEW_UNBLOCK_PRIVATE', data,
                                                        room_id=str(room.id)))

        return data, "Bỏ Chặn thành công", status.HTTP_200_OK


class UpdateNotificationModeInRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request):
        room = Room.objects.get(id=request.query_params.get('room_id'))
        room_user = RoomUser.objects.get(user=request.user,
                                         room=room)
        room_user.notification_mode = request.query_params.get('notification_mode', 'on')
        room_user.save()
        data = ListRoomSerializer(room, context={'request': request}).data
        return data, "Cập nhật thông báo thành công", status.HTTP_200_OK
