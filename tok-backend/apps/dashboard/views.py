import json
from datetime import datetime

from django.contrib.admin import AdminSite
from django.db.models import Count, Prefetch, Q, When, Case, Value
from django.http import JsonResponse
from django.urls import path
from django.shortcuts import render
import matplotlib.pyplot as plt
import io
import base64

from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from apps.blog.models import Blog
from apps.conversation.models import Room, RoomUser, Message
from apps.dashboard.models import FCMToken, NotificationAdmin
from apps.dashboard.serializers import RoomSerializer, NotificationAdminSerializer
from apps.general.models import FileUpload, Report
from apps.payment.models import Transaction
from apps.user.models import CustomUser
from ultis.api_helper import api_decorator
from ultis.helper import get_paginator_limit_offset
from django.contrib.sessions.models import Session


def CSKHView(request):
    if request.method == 'POST':
        pass
    request.user = CustomUser.objects.get(phone_number='+84987654321')
    room_id = RoomUser.objects.select_related('room', 'user').filter(user=request.user,
                                                                     date_removed__isnull=True
                                                                     ).values_list('room', flat=True)
    list_room = Room.objects.prefetch_related(
        Prefetch('roomuser_set', queryset=RoomUser.objects.select_related('user'), to_attr='room_users')).filter(
        id__in=room_id,
        newest_at__isnull=False,
        type='CSKH').order_by(
        '-newest_at')[:10]
    socket_url = f"wss://occo.tokvn.live/conversation/?user_id={str(request.user.id)}"
    list_room_data = RoomSerializer(list_room, context={'request': request}, many=True).data
    return render(request, 'index.html', context={'list_room_data': list_room_data,
                                                  'token': request.user.token,
                                                  'user_id': str(request.user.id),
                                                  'socket_url': socket_url
                                                  })


def user_map(request):
    users = CustomUser.objects.filter(lat__isnull=False, lng__isnull=False, is_fake=False).values('lat', 'lng')
    return render(request, 'user_map.html', {'users': list(users)})


class SearchUserConversationAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        keyword = request.query_params.get('keyword', '')
        request.user = CustomUser.objects.get(phone_number='+84987654321')

        room = Room.objects.filter(Q(roomuser__user=request.user), Q(type='CSKH'))
        room = room.filter(
            (
                    Q(roomuser__user__full_name__icontains=keyword) |
                    Q(roomuser__user__uid__icontains=keyword) |
                    Q(roomuser__user__phone_number__icontains=keyword)
            )
        ).prefetch_related('roomuser_set').distinct().order_by('-newest_at')[:10]

        serializer = RoomSerializer(room, many=True, context={'request': request})

        return serializer.data, 'Danh sách tìm kiếm', status.HTTP_200_OK


class GetListRoomChatOfUserAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def get(self, request):
        request.user = CustomUser.objects.get(phone_number='+84987654321')
        room_id = RoomUser.objects.select_related('room', 'user').filter(user=request.user,
                                                                         date_removed__isnull=True
                                                                         ).values_list('room', flat=True)
        qs = Room.objects.prefetch_related(
            Prefetch('roomuser_set', queryset=RoomUser.objects.select_related('user'), to_attr='room_users')).filter(
            id__in=room_id,
            newest_at__isnull=False,
            type='CSKH').order_by(
            '-newest_at')
        data, paginator = get_paginator_limit_offset(qs, request)
        serializer = RoomSerializer(data, many=True, context={'request': request})
        data_lm = paginator.get_paginated_response(serializer.data).data
        return data_lm, "Danh sách room", status.HTTP_200_OK


class GetUIDAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        session_id = request.COOKIES.get('sessionid')
        if session_id:
            session = Session.objects.get(session_key=session_id)
            user_id = session.get_decoded().get('_auth_user_id')
            user = CustomUser.objects.get(pk=user_id)

            host = request.get_host()
            print(host)

            noti_admin = NotificationAdmin.objects.filter(admin_user=user).order_by('created_at')
            serializer = NotificationAdminSerializer(noti_admin, many=True)
            return {"user_id": str(user.id), "noti_history": serializer.data,
                    "domain": host}, "Thông báo admin", status.HTTP_200_OK
        else:
            return "", "", status.HTTP_200_OK


def statistics_view(request):
    country = request.user.country

    if request.method == 'GET':
        start_date_str = request.GET.get('start_date', "")
        end_date_str = request.GET.get('end_date', "")
        today = datetime.now().date()
        has_filter = False
        if country != 'All':
            filter_user = Q(country=country)
            filter_blog = Q(user__country=country)
            filter_live = Q(host__country=country)
            filter_gift = Q(sender__country=country)
            filter_transaction = Q(from_user__country=country)
            filter_file = Q(owner__country=country)
        else:
            filter_user = Q()
            filter_blog = Q()
            filter_live = Q()
            filter_gift = Q()
            filter_transaction = Q()
            filter_file = Q()

        # user
        new_users_today = CustomUser.objects.all().filter(filter_user).exclude(is_superuser=True)
        online_users = CustomUser.objects.filter(is_online=True, is_fake=False).filter(filter_user).exclude(is_superuser=True)
        band_users = CustomUser.objects.filter(is_active=False).filter(filter_user).exclude(is_superuser=True)
        total_users = CustomUser.objects.filter(is_fake=False).filter(filter_user).exclude(is_superuser=True)
        # blog
        total_blog_posts = Blog.objects.all().filter(filter_blog)
        delete_blog = 0
        new_image = FileUpload.objects.filter(file_type='IMAGE').filter(filter_file).exclude(owner__is_superuser=True)
        new_video = FileUpload.objects.filter(file_type='VIDEO').filter(filter_file).exclude(owner__is_superuser=True)
        blog_report = Report.objects.filter(type='BLOG').filter(filter_blog)

        # payment
        transaction_deposit = Transaction.objects.filter(transaction_type='deposit').filter(filter_transaction)
        transaction_gift = Transaction.objects.filter(transaction_type='gift').filter(filter_transaction)
        transaction_uid = Transaction.objects.filter(transaction_type='uid').filter(filter_transaction)

        if start_date_str:
            has_filter = True

            # user
            start_date = datetime.strptime(start_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            new_users_today = new_users_today.filter(date_joined__date__gte=start_date)
            band_users = band_users.filter(updated_at__date__gte=start_date)

            # blog
            total_blog_posts = total_blog_posts.filter(created_at__date__gte=start_date)
            new_image = new_image.filter(blog__in=total_blog_posts, created_at__date__gte=start_date)
            new_video = new_video.filter(blog__in=total_blog_posts, created_at__date__gte=start_date)
            blog_report = blog_report.filter(created_at__date__gte=start_date)

            # payment
            transaction_deposit = transaction_deposit.filter(created_at__date__gte=start_date)
            transaction_gift = transaction_gift.filter(created_at__date__gte=start_date)
            transaction_uid = transaction_uid.filter(created_at__date__gte=start_date)

        if end_date_str:
            has_filter = True

            # user
            end_date = datetime.strptime(end_date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            new_users_today = new_users_today.filter(date_joined__date__lte=end_date)
            band_users = band_users.filter(updated_at__date__lte=end_date)

            # blog
            total_blog_posts = total_blog_posts.filter(created_at__date__lte=end_date)
            new_image = new_image.filter(blog__in=total_blog_posts, created_at__date__lte=end_date)
            new_video = new_video.filter(blog__in=total_blog_posts, created_at__date__lte=end_date)
            blog_report = blog_report.filter(created_at__date__lte=end_date)

            #payment
            transaction_deposit = transaction_deposit.filter(created_at__date__lte=end_date)
            transaction_gift = transaction_gift.filter(created_at__date__lte=end_date)
            transaction_uid = transaction_uid.filter(created_at__date__gte=end_date)

        if not start_date_str and not end_date_str:
            new_users_today = CustomUser.objects.filter(date_joined__date=today)

        return render(request,
                      'statistics.html',
                      context={
                          'user': request.user,
                          'start_date': start_date_str,
                          'end_date': end_date_str,
                          'has_filter': has_filter,
                          'new_users_today': new_users_today.count(),
                          'online_users': online_users.count(),
                          'band_users': band_users.count(),
                          'total_users': total_users.count(),
                          'total_blog_posts': total_blog_posts.count(),
                          'new_image': new_image.count(),
                          'new_video': new_video.count(),
                          'blog_report': blog_report.count(),

                          'transaction_deposit': transaction_deposit.count(),
                          'transaction_gift': transaction_gift.count(),
                          'transaction_uid': transaction_uid.count(),

                      })
