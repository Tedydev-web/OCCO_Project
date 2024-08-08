from datetime import datetime

from django.db.models import Q, Func, F, FloatField, Value
from django.db.models.expressions import RawSQL, Subquery
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast, Coalesce
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from api.services.firebase import send_not_save_notification
from api.services.telegram import logging
from api.services.telegram_admin import send_telegram_message
from apps.ads.models import Advertisement, AdsTargeting, AdsWallet
from apps.ads.serializers import AdvertisementSerializer, CreateAdvertisementSerializer, UserListAdsSerializer, \
    UpdateAdvertisementSerializer
from apps.dashboard.models import NotificationAdmin
from ultis.api_helper import api_decorator

from ultis.helper import get_paginator_limit_offset


# Target
class GetListAdsForUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        try:
            user = request.user
            today = datetime.now().date()

            # Subquery to exclude ads with views today >= 3
            subquery = AdsTargeting.objects.filter(
                user=user,
                type='view',
                viewed_date__contains={str(today): 3}
            ).values('ads')

            list_exclude = Advertisement.objects.filter(
                id__in=Subquery(subquery)
            ).values_list('id', flat=True)

            age_cond = Q(target__from_age__lte=user.age, target__to_age__gte=user.age)

            # Convert UUIDs to strings for the overlap filter
            habits = [str(habit) for habit in user.baseinformation.habits]
            habit_cond = Q()
            search_cond = Q()
            for habit in habits:
                habit_cond |= Q(target__habit__icontains=habit)
                search_cond |= Q(target__habit__icontains=habit)
            active_cond = Q(is_active=True) & Q(status_verify='verified')
            gender_cond = Q(target__gender__icontains=user.gender)
            date_cond = Q(status_coming='coming')
            platform_cond = Q(platform=user.platform)
            # Use COALESCE to handle NULL values in target__distance
            distance_cond = Q(distance__lte=Coalesce(
                Cast(KeyTextTransform('distance', 'target'), FloatField()),
                Value(float('inf'))))
            qs_default = Advertisement.objects.filter(
                age_cond,
                date_cond,
                active_cond,
                (habit_cond | search_cond),
                platform_cond,
                gender_cond,
            ).exclude(user=user).exclude(id__in=list_exclude)

            qs_distance = qs_default.filter(target__distance__isnull=False, target__lat__isnull=False,
                                            target__lng__isnull=False)
            qs_distance = qs_distance.annotate(
                distance=RawSQL(
                    """
                    SELECT haversine(
                        %s, %s,
                       COALESCE(NULLIF((target->>'lat'), '')::float, 0),
                        COALESCE(NULLIF((target->>'lng'), '')::float, 0)
                    )
                    """,
                    (user.lat, user.lng),
                    output_field=FloatField()
                )
            ).filter(
                distance_cond
            )

            qs_other = qs_default.filter(
                Q(target__country__icontains=user.country) |
                Q(target__province__icontains=user.province)
            ).select_related('image', 'video')

            qs = qs_distance | qs_other
            qs = qs.order_by('-created_at').order_by('?').first()
            if qs:
                target = AdsTargeting.objects.get_or_create(user=request.user, ads=qs)[0]
                target.add_view()
                serializer = UserListAdsSerializer(qs)
                return serializer.data, "Quảng cáo", status.HTTP_200_OK
            else:
                return None, "Không tìm thấy quảng cáo", status.HTTP_200_OK
        except Exception as e:
            logging(e)
            return {str(e)}, "", status.HTTP_400_BAD_REQUEST


class ViewAdsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        ads = Advertisement.objects.get(id=pk)
        target = AdsTargeting.objects.get_or_create(user=request.user, ads=ads)[0]
        target.add_view()
        return {
            "count_view": ads.count_view,
            "count_click": ads.count_click,
        }, "Xem thành công", status.HTTP_200_OK


class ClickAdsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        ads = Advertisement.objects.get(id=pk)
        target = AdsTargeting.objects.get_or_create(user=request.user, ads=ads)[0]
        target.add_click()
        return {
            "count_view": ads.count_view,
            "count_click": ads.count_click,
        }, "Click ads thành công", status.HTTP_200_OK


# Owner
class CreateAdsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        user = request.user
        amount = request.data.get('coin_price')
        wallet = AdsWallet.objects.get_or_create(user=request.user)[0]
        if wallet.current_balance < amount:
            return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

        request.data['user'] = str(user.id)
        request.data['start_date'] = datetime.strptime(request.data['start_date'], '%Y/%m/%d').date()
        request.data['end_date'] = datetime.strptime(request.data['end_date'], '%Y/%m/%d').date()
        serializer = CreateAdvertisementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            ads = Advertisement.objects.get(id=serializer.data['id'])
            data = AdvertisementSerializer(ads).data

            send_not_save_notification(user=request.user,
                                       title='Đặt quảng bá thành công',
                                       body=f'Chiến lược quảng bá đang đợi admin duyệt',
                                       custom_data={
                                           'direct_type': 'ADS_PENDING',
                                           'direct_value': str(ads.id)
                                       })
            url_admin = f"https://occo.tokvn.live/admin/ads/advertisement/{str(ads.id)}/change/"

            notification_admin = NotificationAdmin.objects.create(
                from_user=request.user,
                title=f"{request.user.full_name} đã tạo yêu cầu quảng bá",
                body=f"",
                type='NEW',
                link=url_admin
            )
            send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
            return data, "Tạo quảng cáo thành công", status.HTTP_200_OK
        else:
            return f"{serializer.error_messages}", "Lỗi", status.HTTP_400_BAD_REQUEST


class UpdateAdsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def put(self, request, pk):
        ads = Advertisement.objects.get(id=pk)
        if request.data.get('start_date'):
            request.data['start_date'] = datetime.strptime(request.data['start_date'], '%Y/%m/%d').date()
        if request.data.get('end_date'):
            request.data['end_date'] = datetime.strptime(request.data['end_date'], '%Y/%m/%d').date()
        serializer = UpdateAdvertisementSerializer(ads, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            ads = Advertisement.objects.get(id=serializer.data['id'])
            data = AdvertisementSerializer(ads).data

            return data, "Update thành công và đợi duyệt", status.HTTP_200_OK
        else:
            return f"{str(serializer.errors)}", "Lỗi khi cập nhật", status.HTTP_400_BAD_REQUEST


class DeleteAdsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def delete(self, request, pk):
        ads = Advertisement.objects.get(id=pk)
        ads.delete()
        return {}, "Xoá quảng bá thành công", status.HTTP_200_OK


class DetailAdsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request, pk):
        ads = Advertisement.objects.get(id=pk)
        serializer = AdvertisementSerializer(ads)
        return serializer.data, "Chi tiết quảng cáo", status.HTTP_200_OK


class ListOwnerAdsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        status_coming = request.query_params.get('status_coming', '')
        status_verify = request.query_params.get('status_verify', 'verified')
        qs = Advertisement.objects.filter(user=request.user).filter(
            status_verify=status_verify
        ).order_by('-created_at').select_related('image', 'video')
        if status_coming != '':
            qs.filter(status_coming=status_coming)

        qs, paginator = get_paginator_limit_offset(qs, request)
        serializer = AdvertisementSerializer(qs, many=True)
        data = paginator.get_paginated_response(serializer.data).data
        return data, "Danh sách quảng cáo đã tạo", status.HTTP_200_OK
