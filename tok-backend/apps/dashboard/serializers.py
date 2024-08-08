from rest_framework import serializers

from apps.conversation.models import Room
from apps.conversation.serializers import RoomUserBasicSerializer
from apps.dashboard.models import NotificationAdmin
from apps.user.serializers import UserSerializer


class RoomSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%H:%M %d/%m/%Y", read_only=True)
    newest_at = serializers.DateTimeField(format="%H:%M %d/%m/%Y", read_only=True)

    class Meta:
        model = Room
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        user = self.context.get('request').user

        room_users = instance.roomuser_set.select_related('user', 'user__avatar').all()

        other = next((ru for ru in room_users if ru.user != user), None)

        name = other.user.full_name if other.user.full_name else str(other.user.phone_number)
        image = other.user.get_avatar if other else {'name': '', 'image': ''}

        data['name'] = name
        data['image'] = image

        rs = next((ru for ru in room_users if ru.user == user), None)

        data['total_unseen'] = rs.total_unseen
        data['last_message'] = rs.last_message

        data['list_users'] = RoomUserBasicSerializer(room_users, many=True).data
        data['other'] = UserSerializer(other.user).data
        return data


class NotificationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationAdmin
        fields = ['title', 'body','type', 'link', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['created_at'] = instance.created_at.strftime("%d/%m/%Y %H:%M")
        return data
