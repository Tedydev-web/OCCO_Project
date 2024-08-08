import datetime

from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.timezone import make_aware, is_naive
from rest_framework import serializers

from apps.blog.models import Blog, Comment, ReplyComment, AudioUpload
from apps.general.models import FileUpload
from apps.general.serializers import GetFileUploadSerializer
from apps.user.models import CustomUser, UserVip
from ultis.api_helper import format_time_article


class UserBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id',
                  'full_name',
                  'avatar']

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
        return data


class AudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioUpload
        fields = ['id',
                  'file',
                  'title']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['file'] = str(instance.file.url)

        return data


class BlogSerializer(serializers.ModelSerializer):
    file = GetFileUploadSerializer(many=True)
    user = UserBlogSerializer()
    tagged_users = UserBlogSerializer(many=True)
    audio = AudioSerializer()

    class Meta:
        model = Blog
        fields = ['id', 'user', 'tagged_users', 'created_at', 'title', 'content', 'audio', 'file', 'location',
                  'location_point',
                  'count_comment', 'count_like', 'is_highlight']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['is_liked'] = instance.user_like.filter(id=self.context['request'].user.id).exists()
        data['created_at'] = format_time_article(instance.created_at, timezone.now(), self.context.get('request'))
        return data


class BlogCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), required=True)
    file = serializers.PrimaryKeyRelatedField(queryset=FileUpload.objects.all(), many=True, required=False)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'user', 'audio', 'file', 'content', 'location', 'tagged_users', 'location_point']

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['is_liked'] = False

        return data


class CommentSerializer(serializers.ModelSerializer):
    user = UserBlogSerializer()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'count_like', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        list_reply_comment = instance.replycomment_set.select_related('comment','user').all().order_by('-count_like')
        data['reply_comment'] = ReplyCommentSerializer(list_reply_comment, many=True,
                                                       context={'request': self.context['request']}).data
        data['is_liked'] = instance.user_like.filter(id=self.context['request'].user.id).exists()
        data['created_at'] = format_time_article(instance.created_at, timezone.now(), self.context.get('request'))

        return data


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'blog', 'user', 'content', 'count_like', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_liked'] = False
        return data


class CreateReplyCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyComment
        fields = ['id', 'comment', 'user', 'content', 'count_like', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_liked'] = False
        return data


class ReplyCommentSerializer(serializers.ModelSerializer):
    user = UserBlogSerializer()

    class Meta:
        model = ReplyComment
        fields = ['id', 'user', 'content', 'count_like', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['is_liked'] = instance.user_like.filter(id=self.context['request'].user.id).exists()
        data['created_at'] = format_time_article(instance.created_at, timezone.now(), self.context.get('request'))

        return data
