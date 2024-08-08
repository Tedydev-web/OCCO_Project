import datetime
import os

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from ultis.api_helper import format_time_article
from ultis.user_helper import haversine
from .models import CustomUser, WorkInformation, CharacterInformation, SearchInformation, HobbyInformation, \
    CommunicateInformation, BaseInformation, ProfileImage, FriendShip, Block, Follow, IDCard, UserTimeline, HistorySeen, \
    UserVip
from ..general.models import DefaultAvatar
from ..general.serializers import FileUploadSerializer


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['id',
                  'image']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = str(instance.image.id)
        data['image'] = str(instance.image.file.url)
        return data


class UserSerializer(serializers.ModelSerializer):
    # avatar = FileUploadSerializer()

    class Meta:
        model = CustomUser
        exclude = ['password', 'groups', 'user_permissions']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['avatar'] = instance.get_avatar
        data['avatar_frame'] = instance.get_avatar_frame
        vip = UserVip.objects.get_or_create(user=instance)[0]
        data['is_vip'] = False
        if vip.date_start is not None and vip.date_end :
            if vip.date_end > timezone.now():
                data['is_vip'] = True
        data = instance.check_vip(data)

        data['profile_images'] = ProfileImageSerializer(instance.profileimage_set.all(), many=True).data
        return data


class UserGoogleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'phone_number', 'id', 'register_status']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['avatar'] = instance.get_avatar

        return data


class WorkInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkInformation
        fields = ['id', 'title']


class CharacterInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CharacterInformation
        fields = ['id', 'title']


class SearchInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchInformation
        fields = ['id', 'title']


class HobbyInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HobbyInformation
        fields = ['id', 'title']


class CommunicateInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunicateInformation
        fields = ['id', 'title']


class BaseInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseInformation
        fields = ['search',
                  'work',
                  'character',
                  'hobby',
                  'communicate']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['search'] = SearchInformationSerializer(instance.search, many=True).data
        data['work'] = WorkInformationSerializer(instance.work, many=True).data
        data['character'] = CharacterInformationSerializer(instance.character, many=True).data
        data['hobby'] = HobbyInformationSerializer(instance.hobby, many=True).data
        data['communicate'] = CommunicateInformationSerializer(instance.communicate, many=True).data
        if not any([data['search'], data['work'], data['character'], data['hobby'], data['communicate']]):
            data = []
        return data


class UserFriendShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'full_name',
                  'avatar',
                  'is_online',
                  'is_private',
                  'setting_private']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar_frame'] = instance.get_avatar_frame
        vip = UserVip.objects.get_or_create(user=instance)[0]
        data['is_vip'] = False
        if vip.date_start is not None and vip.date_end :
            if vip.date_end > timezone.now():
                data['is_vip'] = True

        data['avatar'] = instance.get_avatar
        data['is_online'] = instance.is_online
        data['friend'] = None
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
            print(e)
        data = instance.check_vip(data)

        return data


class FriendShipSerializer(serializers.ModelSerializer):
    sender = UserFriendShipSerializer()
    receiver = UserFriendShipSerializer()

    class Meta:
        model = FriendShip
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user_sender = instance.sender
        user_receiver = instance.receiver
        try:
            data['distance'] = haversine(lat1=user_sender.lat,
                                         lat2=user_receiver.lat,
                                         lon1=user_sender.lng,
                                         lon2=user_receiver.lng)
        except Exception as e:
            data['distance'] = None

        return data


class FriendShipUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendShip
        fields = '__all__'


class BaseInforUserSerializer(serializers.ModelSerializer):
    # avatar = FileUploadSerializer()

    class Meta:
        model = CustomUser
        exclude = ['password', 'groups', 'user_permissions', 'social']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['avatar'] = instance.get_avatar
        data['cover_image'] = instance.get_cover_image
        data['avatar_frame'] = instance.get_avatar_frame
        vip = UserVip.objects.get_or_create(user=instance)[0]
        data['is_vip'] = False
        if vip.date_start is not None and vip.date_end :
            if vip.date_end > timezone.now():
                data['is_vip'] = True
        # base information
        try:
            data['base_information'] = BaseInformationSerializer(instance.baseinformation).data
            if data['base_information'] == {}:
                data['base_information'] = None
        except:
            data['base_information'] = None
        # xem profile của chính mình & trường hợp không có request
        data['friend'] = None
        data['distance'] = None
        data['follow'] = None
        data['friend_request'] = None
        data['block_status'] = None
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
                data['block_status'] = CustomUser.custom_objects.is_block(user2=instance,
                                                                          user1=user)
                if user != instance:
                    data = instance.check_vip(data)
        except Exception as e:
            # print("Khong co request duoc truyen vao", e)
            pass
        data['profile_images'] = []
        if ProfileImage.objects.select_related('user').filter(user=instance).exists():
            data['profile_images'] = ProfileImageSerializer(instance.profileimage_set.all(), many=True).data

        return data


class BlockUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'


class FollowUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        print(instance)
        data['from_user'] = UserFriendShipSerializer(instance.from_user).data
        data['to_user'] = UserFriendShipSerializer(instance.to_user).data

        return data


class IDCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = IDCard
        fields = '__all__'


class UserTimeLineSerializer(serializers.ModelSerializer):
    direct_user = UserFriendShipSerializer()

    class Meta:
        model = UserTimeline
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = format_time_article(instance.created_at, timezone.now(), self.context.get('request'))
        return data


class UpdatePrivateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['setting_private','setting_vip','id']


class HistorySeenSerializer(serializers.ModelSerializer):
    class UserBaseSerializer(serializers.ModelSerializer):
        class Meta:
            model = CustomUser
            fields = ['id',
                      'full_name',
                      'avatar']

        def to_representation(self, instance):
            data = super().to_representation(instance)
            data['id'] = str(instance.id)
            data['avatar'] = instance.get_avatar
            data['avatar_frame'] = instance.get_avatar_frame
            vip = UserVip.objects.get_or_create(user=instance)[0]
            data['is_vip'] = False
            if vip.date_start is not None and vip.date_end:
                if vip.date_end > timezone.now():
                    data['is_vip'] = True
            return data

    user_seen = UserBaseSerializer()

    class Meta:
        model = HistorySeen
        fields = ['id', 'created_at', 'user_seen']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = format_time_article(instance.created_at, timezone.now(), self.context.get('request'))
        return data
