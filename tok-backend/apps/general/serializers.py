from rest_framework import serializers

from apps.general.models import FileUpload, Report, FeedBack, CoinTrading, MoneyTrading, Sticker, StickerCategory, \
    AvatarFrame
from ultis.file_helper import format_file_size

from core import settings


class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id',
                  'owner',
                  'file',
                  'file_type',
                  'file_name',
                  'file_url',
                  'file_size',
                  'upload_finished_at',
                  'video_height',
                  'video_width',
                  'file_duration',
                  'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['owner'] = str(instance.owner)
        return data


class GetFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id',
                  'owner',
                  'file',
                  'file_type',
                  'file_name',
                  'file_url',
                  'file_size',
                  'video_height',
                  'video_width',
                  'file_duration',
                  'upload_finished_at',
                  'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['owner'] = str(instance.owner)
        return data


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['file'] = GetFileUploadSerializer(instance.image.all(), many=True).data
        return data


class FeedBackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack
        exclude = ['is_resolve', ]


class CoinTradingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinTrading
        fields = ['id', 'coin_price', 'vnd_price']


class MoneyTradingSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyTrading
        fields = ['id', 'coin_price', 'vnd_price']


class StickerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sticker
        fields = ['id', 'file']


class StickerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StickerCategory
        fields = ['id', 'image']


class AvatarFrameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvatarFrame
        fields = ['id', 'frame', 'coin_price']
