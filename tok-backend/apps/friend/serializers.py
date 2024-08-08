import datetime

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from apps.user.models import CustomUser, BaseInformation, FriendShip, ProfileImage, Follow, UserVip
from apps.user.serializers import BaseInformationSerializer, ProfileImageSerializer, FriendShipSerializer
from ultis.user_helper import haversine


class InforUserSerializer(serializers.ModelSerializer):
    # avatar = FileUploadSerializer()

    class Meta:
        model = CustomUser
        exclude = ['password', 'groups', 'user_permissions', 'is_superuser']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['avatar'] = instance.get_avatar
        data['avatar_frame'] = instance.get_avatar_frame

        # base information
        try:
            data['base_information'] = BaseInformationSerializer(instance.baseinfomation,
                                                                 ).data
            if data['base_information'] == {}:
                data['base_information'] = None
        except:
            data['base_information'] = None

        # xem profile của chính mình & trường hợp không có request
        data['distance'] = None
        data['block_status'] = None
        data['follow'] = None
        data['friend_request'] = None
        try:
            user = self.context['request'].user
            # check friend giữa request.user và instance
            if instance != user:

                try:
                    data['distance'] = haversine(lat1=user.lat,
                                                 lat2=instance.lat,
                                                 lon1=user.lng,
                                                 lon2=instance.lng)
                except Exception as e:
                    data['distance'] = None

                try:
                    data['friend'] = True if str(instance.id) in user.social['friends'] else False
                except:
                    data['friend'] = False
                try:
                    data['friend_request'] = True if str(instance.id) in user.social['friend_request'] else False
                except:
                    data['friend_request'] = False

                try:
                    data['friend_accept'] = True if str(user.id) in instance.social['friend_request'] else False
                except:
                    data['friend_accept'] = False

                try:
                    data['follow'] = True if str(instance.id) in user.social['following'] else False
                except:
                    data['follow'] = False


        except Exception as e:
            ...
        data['profile_images'] = []
        profile_images = instance.profileimage_set.select_related('image').all()
        if profile_images:
            data['profile_images'] = ProfileImageSerializer(profile_images, many=True).data
        vip = UserVip.objects.get_or_create(user=instance)[0]
        data['is_vip'] = False
        if vip.date_start is not None and vip.date_end :
            if vip.date_end > timezone.now():
                data['is_vip'] = True
        data = instance.check_vip(data)
        return data


class InforFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'is_online', 'full_name', 'gender', 'age', 'uid']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar_frame'] = instance.get_avatar_frame

        data['avatar'] = instance.get_avatar
        user = self.context['request'].user
        # check friend giữa request.user và instance
        if instance != user:

            try:
                data['distance'] = haversine(lat1=user.lat,
                                             lat2=instance.lat,
                                             lon1=user.lng,
                                             lon2=instance.lng)
            except Exception as e:
                data['distance'] = None
        vip = UserVip.objects.get_or_create(user=instance)[0]
        data['is_vip'] = False
        if vip.date_start is not None and vip.date_end :
            if vip.date_end > timezone.now():
                data['is_vip'] = True
        data = instance.check_vip(data)
        return data
