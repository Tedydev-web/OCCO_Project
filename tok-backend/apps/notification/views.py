from datetime import datetime

from django.shortcuts import render
from ipware import get_client_ip
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.services.firebase import send_and_save_notification
from apps.notification.models import Notification, UserDevice
from apps.notification.serializers import UserDeviceSerializer, NotificationSerializer
from apps.user.models import CustomUser, UserLog
from ultis.api_helper import api_decorator, activate_language
from ultis.helper import CustomPagination, get_paginator_limit_offset


# Create your views here.

class NotiListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        activate_language(request)
        type_noti = request.query_params.get('type', 'SYSTEM')

        queryset = Notification.objects.filter(user=request.user, type=type_noti).order_by(
            '-created_at').select_related('user')
        queryset, paginator = get_paginator_limit_offset(queryset, request)

        serializer_data = NotificationSerializer(queryset, many=True).data
        paginator_data = paginator.get_paginated_response(serializer_data).data
        return paginator_data, "Retrieve data successfully", status.HTTP_200_OK


class MarkAllReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request):
        queryset = Notification.objects.filter(user=request.user)
        queryset.update(is_read=True)
        return {}, "Đã đọc tất cả thông báo", status.HTTP_200_OK


class MarkReadByIdAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        queryset = Notification.objects.get(id=pk)
        queryset.is_read = True
        queryset.save()
        return {}, "Đã đọc thông báo", status.HTTP_200_OK


class SubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, *args, **kwargs):
        user = self.request.user
        token = self.request.data.get('token')
        name = self.request.data.get('name')
        model = self.request.data.get('model')

        # Kiểm tra xem device đã tồn tại hay chưa
        existing_device = UserDevice.objects.filter(token=token).first()
        if existing_device:
            return {}, "Token đã được đăng ký với user khác", status.HTTP_204_NO_CONTENT

        device_serializer = UserDeviceSerializer(data=request.data, context={'request': request}, partial=True)
        if device_serializer.is_valid(raise_exception=True):
            device_serializer.save(user=user, token=token, name=name, model=model)
            return device_serializer.data, "Đăng ký nhận thông báo thành công", status.HTTP_200_OK
        else:
            return {}, "Token không hợp lệ", status.HTTP_400_BAD_REQUEST


class UnsubscribeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, *args, **kwargs):
        user = self.request.user
        token = self.request.data.get('token')

        if UserDevice.objects.filter(token=token, user=user).exists():
            device = UserDevice.objects.get(token=token, user=user)
            device.delete()
            user_log = UserLog.objects.get_or_create(user=str(user.id), phone_number=str(user.phone_number))[0]
            ipaddr = get_client_ip(request)[0]
            user_log.logout.append({
                'ipaddr': ipaddr,
                'date': str(datetime.now()),
            })
            user_log.save()
        return {}, "Unsubscribe notification successfully", status.HTTP_200_OK


class SendPushNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, *args, **kwargs):
        user = self.request.user

        title = self.request.data.get('title')
        body = self.request.data.get('body')
        cus_data = request.data.get('data', None)
        direct_type = "Test"
        direct_value = "Test"

        if not title or not body:
            raise ValueError("Title/body is not empty")

        notification = send_and_save_notification(user,
                                                  title,
                                                  body,
                                                  direct_type,
                                                  direct_value,
                                                  None,
                                                  custom_data=cus_data)

        notification_serializer = NotificationSerializer(notification)

        return notification_serializer.data, "Push notification sent and saved successfully", status.HTTP_200_OK


class SendPushAllNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, *args, **kwargs):

        title = request.data.get('title')
        body = request.data.get('body')
        cus_data = request.data.get('data', None)
        direct_type = "Test"
        direct_value = "Test"

        if not title or not body:
            raise ValueError("Title/body is not empty")

        users = CustomUser.objects.all()
        for user in users:
            notification = send_and_save_notification(user,
                                                      title,
                                                      body,
                                                      direct_type,
                                                      direct_value,
                                                      None,
                                                      custom_data=cus_data)

        return {}, "Push all notification sent and saved successfully", status.HTTP_200_OK


class CountUnReadNotificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        queryset = Notification.objects.filter(user=request.user, is_read=False).count()
        return {'len_unread': queryset}, "Count un-read notification success!", status.HTTP_200_OK
