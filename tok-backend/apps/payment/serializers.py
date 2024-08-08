from rest_framework import serializers

from apps.general.models import UIDTrading, Vip
from apps.payment.models import Transaction, Banking, VIPLog
from apps.user.models import UserVip


class TransactionSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True, format='%d-%m-%Y %H:%M:%S')

    class Meta:
        model = Transaction
        exclude = ['from_user',
                   'to_user',
                   'updated_at']


class UIDTradingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UIDTrading
        fields = ['id', 'uid', 'coin_price']


class MBBankInfoSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%H:%M %d/%m/%Y")

    class Meta:
        model = Banking
        fields = ['id',
                  "bank_code",
                  "bin_card",
                  "fullname",
                  "short_name",
                  "icon",
                  'created_at']


class VipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vip
        fields = "__all__"


class VipLogSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d/%m/%Y - %H:%M")

    class Meta:
        model = VIPLog
        fields = ['created_at', 'vip']


class UserVipSerializer(serializers.ModelSerializer):
    vip = VipSerializer()
    date_start = serializers.DateTimeField(format="%d/%m/%Y - %H:%M")
    date_end = serializers.DateTimeField(format="%d/%m/%Y - %H:%M")

    class Meta:
        model = UserVip
        fields = ['date_start', 'date_end', 'vip']
