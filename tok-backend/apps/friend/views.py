from itertools import chain

from django.contrib.postgres.lookups import Unaccent
from django.db.models import Q, F, ExpressionWrapper, FloatField, Func
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.services.firebase import send_not_save_notification
from apps.friend.serializers import InforUserSerializer, InforFriendSerializer
from apps.user.models import FriendShip, CustomUser, Block, Follow
from apps.user.serializers import FriendShipSerializer, UserFriendShipSerializer, UserSerializer, \
    BaseInforUserSerializer
from ultis.api_helper import api_decorator
from ultis.helper import get_paginator_limit_offset
from ultis.socket_friend_helper import send_noti_add_friend, send_noti_accept_friend
from ultis.socket_helper import send_noti_to_socket_user, get_socket_data
from ..user.tasks import remove_relation_ship, remove_relation_ship_sender


# Create your views here.
class RequestFriendShipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        list_request_friend_ship = FriendShip.objects.filter(receiver=request.user,
                                                             status='PENDING').order_by('-created_at').select_related(
            'sender', 'receiver')

        serializer = FriendShipSerializer(list_request_friend_ship, many=True, context={'request': request})

        return serializer.data, 'Danh sách lời mời kết bạn!', status.HTTP_200_OK


class ListFriendShipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        user = CustomUser.objects.get(id=pk)
        accepted_friendships = CustomUser.objects.filter(id__in=list(user.social.get('friends', [])))

        qs, paginator = get_paginator_limit_offset(accepted_friendships, request)

        serializer = UserFriendShipSerializer(qs, many=True, context={'request': request})

        data = paginator.get_paginated_response(serializer.data).data

        return data, 'Danh sách bạn bè!', status.HTTP_200_OK


class AddFriendShipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        receiver = CustomUser.objects.get(id=user_id)

        if CustomUser.custom_objects.is_block(request.user, receiver) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        friend_ship = FriendShip.objects.select_related('sender', 'receiver').filter(
            Q(sender=request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=request.user)).first()

        follow, created = Follow.objects.get_or_create(from_user=request.user, to_user=receiver)

        request.user.add_following(receiver.id)
        receiver.add_follower(str(request.user.id))

        if friend_ship:  # đã từng gửi yêu cầu nhưng bị hủy kết bạn hoặc từ chối sẽ vào case này
            friend_ship.sender = request.user
            friend_ship.receiver = receiver
            friend_ship.save()

            if friend_ship.status == 'PENDING':

                serializer = FriendShipSerializer(friend_ship, context={'request': request})
                return serializer.data, 'Đã gửi yêu cầu kết bạn rồi. Vui lòng đợi phản hồi!', status.HTTP_200_OK

            elif friend_ship.status == 'ACCEPTED':
                serializer = FriendShipSerializer(friend_ship, context={'request': request})
                return serializer.data, 'Các bạn đã là bạn bè!', status.HTTP_200_OK

            else:
                friend_ship.status = 'PENDING'
                friend_ship.save()
                request.user.plus_friend_request(receiver.id)
                receiver.plus_friend_accept(request.user.id)

                send_noti_add_friend(request.user, receiver)
                serializer = FriendShipSerializer(friend_ship, context={'request': request})
                return serializer.data, 'Gửi yêu cầu kết bạn thành công!', status.HTTP_200_OK

        else:
            receiver.plus_friend_accept(request.user.id)
            request.user.plus_friend_request(receiver.id)
            request.user.add_following(receiver.id)
            receiver.add_follower(str(request.user.id))

            friend_ship = FriendShip.objects.create(sender=request.user, receiver=receiver)
            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            send_noti_add_friend(request.user, receiver)

            return serializer.data, 'Gửi yêu cầu kết bạn thành công!', status.HTTP_200_OK


class AcceptFriendByUserIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        receiver = CustomUser.objects.get(id=user_id)
        if CustomUser.custom_objects.is_block(request.user, receiver) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        friend_ship = FriendShip.objects.select_related('sender', 'receiver').filter(
            Q(sender=request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=request.user),
            status='PENDING').first()
        if friend_ship:
            follow, created = Follow.objects.get_or_create(from_user=request.user, to_user=receiver)

            receiver.add_follower(request.user.id)
            request.user.add_following(receiver.id)

            friend_ship.status = 'ACCEPTED'
            friend_ship.save()

            request.user.plus_count_friend(receiver.id)
            receiver.plus_count_friend(request.user.id)
            request.user.minus_friend_request(receiver.id)
            receiver.minus_friend_request(request.user.id)
            request.user.minus_friend_accept(receiver.id)

            send_noti_accept_friend(receiver, request.user)

            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Đã chấp nhận lời mời kết bạn!', status.HTTP_200_OK
        else:
            return {}, 'Chưa yêu cầu kết bạn!', status.HTTP_400_BAD_REQUEST


class RejectFriendByUserIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')
        receiver = CustomUser.objects.get(id=user_id)

        if CustomUser.custom_objects.is_block(request.user, receiver) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        queryset = FriendShip.objects.select_related('sender', 'receiver').filter(
            Q(sender=request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=request.user),
            status='PENDING')

        if queryset.exists():
            friend_ship = queryset[0]

            request.user.minus_friend_request(user_id)
            receiver.minus_friend_request(str(request.user.id))
            request.user.minus_friend_accept(receiver.id)

            request.user.remove_follower(str(friend_ship.sender.id))
            receiver.remove_following(str(request.user.id))

            remove_relation_ship_sender.s(str(receiver.id), str(request.user.id))

            friend_ship.status = 'REJECTED'
            friend_ship.save()
            serializer = FriendShipSerializer(friend_ship, context={'request': request})
            return serializer.data, 'Từ chối kết bạn thành công!', status.HTTP_200_OK
        else:
            return {}, 'Yêu cầu kết bạn không tồn tại!', status.HTTP_400_BAD_REQUEST


class DeleteFriendByUserIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request):
        user_id = request.data.get('user_id')
        receiver = CustomUser.objects.get(id=user_id)
        if CustomUser.custom_objects.is_block(request.user, receiver) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        queryset = FriendShip.objects.select_related('sender', 'receiver').filter(
            Q(sender=request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=request.user),
            status='ACCEPTED')
        if queryset.exists():
            friend_ship = queryset[0]
            friend_ship.status = 'DELETED'
            friend_ship.save()

            remove_relation_ship.s(str(friend_ship.receiver.id), str(friend_ship.sender.id)).apply_async(countdown=0)

            request.user.remove_relationship(str(receiver.id))
            receiver.remove_relationship(str(request.user.id))

            send_noti_to_socket_user(str(request.user.id),
                                     get_socket_data('NEW_FRIEND_DELETE', str(receiver.id)))
            send_noti_to_socket_user(str(receiver.id),
                                     get_socket_data('NEW_FRIEND_DELETE', str(request.user.id)))

            return {}, 'Xóa thành công!', status.HTTP_204_NO_CONTENT
        else:
            return {}, 'Chưa kết bạn!', status.HTTP_400_BAD_REQUEST


class IsFriendAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        user_id = request.data.get('user_id')
        receiver = CustomUser.objects.get(id=user_id)
        if CustomUser.custom_objects.is_block(request.user, receiver) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        queryset = FriendShip.objects.filter(Q(sender=request.user, receiver_id=user_id) |
                                             Q(sender_id=user_id, receiver=request.user),
                                             status='ACCEPTED').exists()
        if queryset:
            return True, 'Là bạn bè!', status.HTTP_200_OK
        else:
            return False, 'Chưa là bạn bè!', status.HTTP_400_BAD_REQUEST

    # =======================  Recommended =============================


class FriendCommendedAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        id_friend_and_me = chain(list(request.user.social.get('friends', [])), [str(request.user.id)])
        r_qs = CustomUser.custom_objects.recommend_users_and_weight(request.user).exclude(Q(setting_private__hide_recommend_friend=True) |
                                                                                          Q(is_superuser=True)).exclude(id__in=id_friend_and_me)
        final_data, paginator = get_paginator_limit_offset(r_qs, request)

        serializer = InforFriendSerializer(final_data, many=True, context={'request': request})
        paginator_data = paginator.get_paginated_response(serializer.data).data

        return paginator_data, "Danh sách đề cử", status.HTTP_200_OK


class FriendNearbyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        id_friend_and_me = chain(list(request.user.social.get('friends', [])), [str(request.user.id)])
        list_user_no_block = CustomUser.custom_objects.filter_blocked_users(request.user).exclude(
            id__in=id_friend_and_me).exclude(Q(setting_private__hide_location=True) |
                                             Q(is_superuser=True))

        gender = request.query_params.get('gender_list').split(',') if request.query_params.get('gender_list') else None
        from_age = request.query_params.get('from_age', None)
        to_age = request.query_params.get('to_age', None)
        from_height = request.query_params.get('from_height', None)
        to_height = request.query_params.get('to_height', None)
        from_weight = request.query_params.get('from_weight', None)
        to_weight = request.query_params.get('to_weight', None)
        from_distance = request.query_params.get('from_distance', 0)
        to_distance = request.query_params.get('to_distance', 20)
        search = request.query_params.get('search').split(',') if request.query_params.get('search') else None

        list_user_no_block = list_user_no_block.filter(
            baseinformation__search__id__in=search).distinct() if search else list_user_no_block

        list_user_no_block = list_user_no_block.filter(gender__in=gender) if gender else list_user_no_block

        list_user_no_block = list_user_no_block.filter(
            age__range=[int(from_age), int(to_age)]) if from_age else list_user_no_block

        list_user_no_block = list_user_no_block.filter(
            height__range=[int(from_height), int(to_height)]) if from_height else list_user_no_block

        list_user_no_block = list_user_no_block.filter(
            weight__range=[int(from_weight), int(to_weight)]) if from_weight else list_user_no_block

        user_lat = request.user.lat
        user_lng = request.user.lng

        if user_lat and user_lng:
            # Annotate the queryset with distance
            list_user_no_block = list_user_no_block.annotate(
                distance=Func(F('lat'), F('lng'), float(user_lat), float(user_lng), function='haversine')
            ).filter(distance__range=[float(from_distance), float(to_distance)]).order_by('distance')

            final_data, paginator = get_paginator_limit_offset(list_user_no_block, request)
            serializer_data = InforFriendSerializer(final_data, many=True, context={'request': request}).data
            paginator_data = paginator.get_paginated_response(serializer_data).data

            return paginator_data, "Danh sách gần đây", status.HTTP_200_OK

        else:  # filter theo tỉnh

            list_user_no_block = list_user_no_block.filter(province=request.user.province)
            final_data, paginator = get_paginator_limit_offset(list_user_no_block, request)

            serializer_data = InforFriendSerializer(final_data, many=True, context={'request': request}).data
            paginator_data = paginator.get_paginated_response(serializer_data).data

            return paginator_data, "Danh sách gần đây", status.HTTP_200_OK


class FriendMatchAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        id_friend_and_me = chain(list(request.user.social.get('friends', [])), [str(request.user.id)])
        qs_match = CustomUser.custom_objects.recommend_users(request.user).exclude(id__in=id_friend_and_me).exclude(Q(setting_private__hide_match_friend=True) |
                                                                                   Q(is_superuser=True))
        qs, paginator = get_paginator_limit_offset(qs_match, request)
        serializer = InforUserSerializer(qs, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer.data).data
        return data, "Danh sách ghép đôi", status.HTTP_200_OK


class FindUserByFullName(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        keyword = request.query_params.get('keyword')
        user_rs = CustomUser.custom_objects.filter_blocked_users(request.user).select_related('avatar')
        final_queryset = user_rs.annotate(
            unaccented_full_name=Unaccent(F('full_name')),
            unaccented_uid=Unaccent(F('uid'))
        ).filter(
            Q(unaccented_full_name__icontains=keyword) |
            Q(unaccented_uid__icontains=keyword)
        ).exclude(id=request.user.id).exclude(Q(is_superuser=True)).exclude(setting_vip__prevent_search=True)
        user, paginator = get_paginator_limit_offset(final_queryset, request)
        serializer = InforFriendSerializer(user, many=True, context={'request': request})
        data = paginator.get_paginated_response(serializer.data).data
        return data, 'Danh sách kết quả', status.HTTP_200_OK


class RevokeRequestFriendByUserID(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user_id = request.data.get('user_id')

        receiver = CustomUser.objects.get(id=user_id)
        if CustomUser.custom_objects.is_block(request.user, receiver) is not None:
            return {}, "Người dùng không tồn tại", status.HTTP_400_BAD_REQUEST

        friend_ship = FriendShip.objects.select_related('sender', 'receiver').filter(
            Q(sender=request.user, receiver_id=user_id) |
            Q(sender_id=user_id, receiver=request.user)).first()

        if friend_ship.status == 'REJECTED':
            return {}, 'Đối phương đã từ chối kết bạn!', status.HTTP_400_BAD_REQUEST

        elif friend_ship.status == 'ACCEPTED':
            return {}, 'Đối phương đã chấp nhận lời mời kết bạn!', status.HTTP_400_BAD_REQUEST

        else:
            try:
                friend_ship.status = 'DELETED'
                friend_ship.save()

                request.user.remove_following(str(receiver.id))
                receiver.remove_follower(str(request.user.id))
                request.user.minus_friend_request(str(receiver.id))
                receiver.minus_friend_request(str(request.user.id))

                remove_relation_ship_sender.s(str(request.user.id), str(receiver.id)).apply_async(
                    countdown=0)

                serializer = FriendShipSerializer(friend_ship, context={'request': request})
                return serializer.data, 'Thu hồi lời mời kết bạn thành công!', status.HTTP_200_OK
            except:
                return {}, 'Thu hồi lời mời kết bạn thành công!', status.HTTP_200_OK
