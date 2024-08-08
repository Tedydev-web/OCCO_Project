import datetime

from rest_framework import serializers

from api.services.firebase import send_not_save_notification
from api.services.telegram_admin import send_telegram_message
from apps.ads.models import Advertisement, RateCoinPerView
from apps.dashboard.models import NotificationAdmin
from apps.general.serializers import FileUploadSerializer
from apps.user.models import HobbyInformation, SearchInformation
from apps.user.serializers import HobbyInformationSerializer, SearchInformationSerializer


class AdvertisementSerializer(serializers.ModelSerializer):
    image = FileUploadSerializer()
    video = FileUploadSerializer()
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    start_date = serializers.DateField(format="%d/%m/%Y")
    end_date = serializers.DateField(format="%d/%m/%Y")
    user = serializers.CharField(source='user.id', read_only=True)

    class Meta:
        model = Advertisement
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['count_view'] = instance.count_view
        data['count_click'] = instance.count_click
        data['target']['habit'] = HobbyInformationSerializer(
            HobbyInformation.objects.filter(id__in=instance.target.get('habit', [])), many=True).data
        data['target']['search'] = SearchInformationSerializer(
            SearchInformation.objects.filter(id__in=instance.target.get('search', [])), many=True).data
        return data


class CreateAdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        current_ratio = RateCoinPerView.objects.first().coin

        instance.maximum_view = int(instance.coin_price / current_ratio)
        data['maximum_view'] = instance.maximum_view

        today = datetime.datetime.now().date()
        if today == instance.start_date:
            instance.status_coming = 'coming'

        instance.save()

        return data


class UpdateAdvertisementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        current_ratio = RateCoinPerView.objects.first().coin

        instance.maximum_view = int(instance.coin_price / current_ratio)
        data['maximum_view'] = instance.maximum_view

        today = datetime.datetime.now().date()
        if today == instance.start_date:
            instance.status_coming = 'coming'

        instance.status_verify = 'pending'
        instance.save()
        url_admin = f"https://occo.tokvn.live/admin/ads/advertisement/{str(instance.id)}/change/"

        notification_admin = NotificationAdmin.objects.create(
            from_user=instance.user,
            title=f"{instance.user.full_name} đã cập nhật quảng bá",
            body=f"",
            type='NEW',
            link=url_admin
        )
        send_not_save_notification(user=instance.user,
                                   title='Cập nhật quảng bá thành công',
                                   body=f'Chiến lược quảng bá đang đợi admin duyệt',
                                   custom_data={
                                       'direct_type': 'ADS_PENDING',
                                       'direct_value': str(instance.id)
                                   })

        send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
        return data


class UserListAdsSerializer(serializers.ModelSerializer):
    image = FileUploadSerializer()
    video = FileUploadSerializer()
    created_at = serializers.DateTimeField(format="%d/%m/%Y %H:%M:%S")
    start_date = serializers.DateField(format="%d/%m/%Y")
    end_date = serializers.DateField(format="%d/%m/%Y")
    user = serializers.CharField(source='user.id', read_only=True)

    class Meta:
        model = Advertisement
        exclude = ['target', 'coin_price', 'maximum_view', ]
