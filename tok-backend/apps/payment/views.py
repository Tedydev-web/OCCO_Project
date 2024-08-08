import base64
import datetime
import time

from django.shortcuts import render

from django.http import HttpResponse
import json

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.services.appota import AppotaService, decode_result_data
from api.services.firebase import send_and_save_notification, send_not_save_notification
from api.services.google import get_service_account_token, \
    get_data_from_api
from api.services.telegram import logging
from api.services.telegram_admin import send_telegram_message
from apps.ads.models import AdsWallet, Advertisement
from apps.conversation.models import Room, Message
from apps.conversation.task import send_new_message_to_room
from apps.dashboard.models import NotificationAdmin
from apps.discovery.models import Gift, UserGift, GiftLog
from apps.discovery.serializers import UserGiftSerializer, GiftLogSerializer, GiftSerializer
from apps.general.models import CoinTrading, AppConfig, MoneyTrading, UIDTrading, AvatarFrame, Vip
from apps.general.serializers import CoinTradingSerializer, MoneyTradingSerializer, AvatarFrameSerializer
from apps.payment.models import Wallet, Transaction, Banking, VIPLog
from apps.payment.serializers import TransactionSerializer, UIDTradingSerializer, MBBankInfoSerializer, VipSerializer, \
    VipLogSerializer, UserVipSerializer
from apps.payment.tasks import check_timeout_payment, send_vip_expiration_reminder, reset_vip_settings
from apps.user.models import CustomUser, UserVip
from ultis.api_helper import api_decorator
from ultis.helper import get_paginator_limit_offset


class BuyCoinAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @api_decorator
    def post(self, request):
        coin_id = request.query_params.get('coin_id')
        coin = CoinTrading.objects.get(id=coin_id)
        coin_data = CoinTradingSerializer(coin).data

        trans = Transaction.objects.create(from_user=request.user,
                                           funds='Appota',
                                           transaction_type='deposit',
                                           amount=coin.vnd_price,
                                           return_code='02'
                                           )
        trans.add_item_detail(coin_data)
        trans.add_from_user_data(str(request.user.id))

        app = AppotaService()
        try:
            appota_payment = app.create_order(transaction=trans)
            check_timeout_payment.s(str(trans.id)).apply_async(countdown=60 * 15)
            return appota_payment['payment']['url'], "Link thanh toán", status.HTTP_200_OK

        except Exception as e:
            logging(e)
            return {}, "Đã xảy ra lỗi, vui lòng thử lại sau", status.HTTP_400_BAD_REQUEST


class CurrentCoinAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @api_decorator
    def get(self, request):
        my_wallet = Wallet.objects.get_or_create(user=request.user)[0]
        ads_wallet = AdsWallet.objects.get_or_create(user=request.user)[0]
        return {"coin": my_wallet.current_balance,
                "ads_coin": round(ads_wallet.current_balance, 2)}, "Thóc hiện tại", status.HTTP_200_OK


class ListCoinBuyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        list_coin = CoinTrading.objects.filter(is_active=True).order_by('coin_price')
        data = CoinTradingSerializer(list_coin, many=True).data
        return data, "Danh sách quy đổi", status.HTTP_200_OK


class ListMoneyTradingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        list_coin = MoneyTrading.objects.filter(is_active=True).order_by('coin_price')
        data = MoneyTradingSerializer(list_coin, many=True).data
        return data, "Danh sách quy đổi", status.HTTP_200_OK


class BuyGiftAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        gift = Gift.objects.get(id=pk)
        amount = int(request.query_params.get('amount'))
        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        if wallet.current_balance < gift.price * amount:
            return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

        user_gift = UserGift.objects.get_or_create(user=request.user,
                                                   gift=gift)[0]
        user_gift.add_quantity(amount)
        wallet.subtract_balance(gift.price * amount)
        trans = Transaction.objects.create(from_user=request.user,
                                           funds='Coin',
                                           transaction_type='gift',
                                           amount=gift.price,
                                           return_code='00'
                                           )
        data_trade = GiftSerializer(gift).data
        trans.add_detail("gift", data_trade)
        send_and_save_notification(user=request.user,
                                   title='Quy đổi thóc sang quà thành công',
                                   body=f"Số dư thóc hiện tại: {wallet.current_balance}",
                                   direct_type='BUY_GIFT_SUCCESS')
        serializer = UserGiftSerializer(user_gift)
        return serializer.data, "Mua thành công", status.HTTP_200_OK


class TradeGiftToCoinAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        gift = Gift.objects.get(id=request.query_params.get('gift_id'))
        amount = int(request.query_params.get('amount'))
        wallet = Wallet.objects.get_or_create(user=request.user)[0]

        user_gift = UserGift.objects.get_or_create(user=request.user,
                                                   gift=gift)[0]
        if user_gift.quantity < amount:
            return {}, "Số lượng quà hiện tại không đủ", status.HTTP_400_BAD_REQUEST

        user_gift.sub_quantity(amount)
        wallet.add_balance(gift.price * amount)
        serializer = UserGiftSerializer(user_gift)
        send_and_save_notification(user=request.user,
                                   title='Đổi quà sang thóc thành công',
                                   body=f"Số dư thóc hiện tại: {wallet.current_balance}",
                                   direct_type='TRADE_GIFT_SUCCESS')

        return serializer.data, "Đổi thóc thành công", status.HTTP_200_OK


class WithdrawCoinAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        coin_id = request.query_params.get('coin_id')
        money_trade = MoneyTrading.objects.get(id=coin_id)
        bank = Banking.objects.get(id=request.query_params.get('bank_id'))
        withdraw_info = {
            'bank_account': request.query_params.get("bank_account"),
            "account_name": request.query_params.get("account_name")
        }
        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        if wallet.current_balance < money_trade.coin_price:
            return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

        trans = Transaction.objects.create(from_user=request.user,
                                           funds='Coin',
                                           transaction_type='withdraw',
                                           amount=money_trade.coin_price,
                                           return_code='02'
                                           )
        data_trade = MoneyTradingSerializer(money_trade).data
        trans.add_item_detail(data_trade)
        print(trans.information_detail['item_data'])
        banking = MBBankInfoSerializer(bank).data
        trans.add_detail('banking', banking)
        wallet.subtract_balance(money_trade.coin_price)
        trans.add_detail("user_info", withdraw_info)
        trans.add_detail("from_user", str(request.user.id))
        send_and_save_notification(user=request.user,
                                   title='Tạo yêu cầu rút thóc thành công',
                                   body=f"Số dư thóc hiện tại: {wallet.current_balance}",
                                   direct_type='WITHDRAW_PENDING')

        url_admin = f"https://occo.tokvn.live/admin/payment/transaction/{str(trans.id)}/change/"
        notification_admin = NotificationAdmin.objects.create(
            from_user=request.user,
            title=f"{request.user.full_name} đã tạo yêu cầu rút tiền",
            body=f"",
            type='NEW',
            link=url_admin
        )
        send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)

        return {'coin': wallet.current_balance}, "Đã gửi yêu cầu rút thóc", status.HTTP_200_OK


class HistoryTransactionCoinAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        transactions = Transaction.objects.filter(from_user=request.user).order_by('-created_at')
        qs, paginator = get_paginator_limit_offset(transactions, request)
        serializer = TransactionSerializer(qs, many=True)
        data = paginator.get_paginated_response(serializer.data).data
        return data, "Lịch sử", status.HTTP_200_OK


class HistoryTransactionGiftAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        gifts = GiftLog.objects.filter(sender=request.user).order_by('-created_at')

        serializer = GiftLogSerializer(gifts, many=True)
        return serializer.data, "Lịch sử", status.HTTP_200_OK


class SendGiftToUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        amount = int(request.query_params.get('amount'))
        sender = request.user
        receiver = request.query_params.get('receiver_id').split(',')
        receiver = CustomUser.objects.filter(id__in=receiver)
        gift_send = Gift.objects.get(id=request.query_params.get('gift_id'))
        user_gift = UserGift.objects.get_or_create(user=request.user,
                                                   gift=gift_send)[0]
        if user_gift.quantity < amount * len(receiver):
            quantity_need = amount - user_gift.quantity
            wallet = Wallet.objects.get_or_create(user=request.user)[0]
            if wallet.current_balance < gift_send.price * quantity_need:
                return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

            user_gift.add_quantity(quantity_need)
            wallet.subtract_balance(gift_send.price * quantity_need)
            trans = Transaction.objects.create(from_user=request.user,
                                               funds='Coin',
                                               transaction_type='gift',
                                               amount=gift_send.price,
                                               return_code='00'
                                               )
            data_trade = GiftSerializer(gift_send).data
            trans.add_detail("gift", data_trade)

        gift = GiftLog.objects.create(gift=gift_send,
                                      sender=sender,
                                      amount=amount,
                                      place='CHAT'
                                      )
        gift.receiver.set(receiver)
        gift.save()
        room_id = request.query_params.get('room_id', '')
        room = Room.objects.get(id=room_id)
        receiver_name = "cho " + ", ".join(
            receiver.values_list('full_name', flat=True)) if room.type == 'GROUP' else ""
        sender_name = "Người dùng ẩn danh" if room.type == 'PRIVATE' else sender.full_name

        for receiver_gift in gift.receiver.all():
            UserGift.objects.get_or_create(gift=gift_send, user=receiver_gift)[0].add_quantity(gift.amount)
            user_gift.sub_quantity(gift.amount)
            send_not_save_notification(user=receiver_gift,
                                       title='Thông báo',
                                       body=f"{sender_name} vừa gửi cho bạn {amount} {gift.gift.title}")

        msg = Message.objects.create(sender=sender,
                                     gift=gift,
                                     type='GIFT',
                                     text=f'{sender_name} đã tặng {amount} {gift_send.title} {receiver_name}',
                                     room=room)
        send_new_message_to_room.s(str(room.id), str(msg.id), str(request.user.id)).apply_async(countdown=0)

        # UserGift.objects.get_or_create(gift=gift_send, user=receiver[0])[0].add_quantity(gift.amount)
        # user_gift.sub_quantity(gift.amount)

        serializer = UserGiftSerializer(user_gift, context={'request': request})
        data = serializer.data

        return data, "Gửi quà thành công", status.HTTP_200_OK


class ListUIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        qs = UIDTrading.objects.filter(is_active=True).order_by('-coin_price')

        serializer = UIDTradingSerializer(qs, many=True)
        return serializer.data, "Danh sách uid", status.HTTP_200_OK


class BuyUIDAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        uid = UIDTrading.objects.get(id=pk)
        if not uid.is_active:
            return {}, "Uid đã bị mua mất rồi", status.HTTP_400_BAD_REQUEST

        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        if wallet.current_balance < uid.coin_price:
            return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

        trans = Transaction.objects.create(from_user=request.user,
                                           funds='Coin',
                                           transaction_type='uid',
                                           amount=uid.coin_price,
                                           return_code='00'
                                           )
        data_trade = UIDTradingSerializer(uid).data
        trans.add_detail("uid", data_trade)
        wallet.subtract_balance(uid.coin_price)
        send_and_save_notification(user=request.user,
                                   title='Mua uid thành công',
                                   body=f"Số dư thóc hiện tại: {wallet.current_balance}",
                                   direct_type='BUY_UID_SUCCESS')
        request.user.uid = uid.uid
        request.user.save()

        uid.is_active = False
        uid.save()
        return {
            'uid': uid.uid,
            'coin': wallet.current_balance
        }, "Mua thành công uid", status.HTTP_200_OK


class BuyAvatarFrameAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        avt = AvatarFrame.objects.get(id=pk)
        if not avt.is_active:
            return {}, "Avatar đã bị tắt bởi admin", status.HTTP_400_BAD_REQUEST

        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        if wallet.current_balance < avt.coin_price:
            return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

        trans = Transaction.objects.create(from_user=request.user,
                                           funds='Coin',
                                           transaction_type='avatar',
                                           amount=avt.coin_price,
                                           return_code='00'
                                           )
        data_trade = AvatarFrameSerializer(avt).data
        trans.add_detail("avt", data_trade)
        wallet.subtract_balance(avt.coin_price)
        send_and_save_notification(user=request.user,
                                   title='Mua khung avatar thành công',
                                   body=f"Số dư thóc hiện tại: {wallet.current_balance}",
                                   direct_type='BUY_AVT_SUCCESS')
        request.user.avatar_frame = avt
        request.user.save()

        return {
            'avatar_frame': request.user.get_avatar_frame,
            'coin': wallet.current_balance
        }, "Mua khung avatar thành công", status.HTTP_200_OK


class TradeCoinToAdsWalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        amount = int(request.query_params.get('coin_price'))
        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        ads_wallet = AdsWallet.objects.get_or_create(user=request.user)[0]
        if wallet.current_balance < amount:
            return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

        trans = Transaction.objects.create(from_user=request.user,
                                           funds='Coin',
                                           transaction_type='coinToAds',
                                           amount=amount,
                                           return_code='00'
                                           )
        trans.add_detail("coinToAds", {'coin_price': amount})
        wallet.subtract_balance(amount)
        ads_wallet.add_balance(amount)

        send_and_save_notification(user=request.user,
                                   title='Chuyển thóc sang ví quảng cáo thành công',
                                   body=f"Số dư thóc hiện tại: {wallet.current_balance}",
                                   direct_type='TRADE_COIN_TO_ADS_SUCCESS')
        if ads_wallet.current_balance > 0:
            ads_invalid = Advertisement.objects.filter(user=request.user,
                                                       is_active=False,
                                                       status_coming='coming',
                                                       status_verify='verified').update(is_active=True)

        return {
            'coin': wallet.current_balance,
            'ads_coin': round(ads_wallet.current_balance, 2)
        }, "Đổi thóc sang ví quảng cáo thành công", status.HTTP_200_OK


class CurrentCoinAdsWalletAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @api_decorator
    def get(self, request):
        my_waller = AdsWallet.objects.get_or_create(user=request.user)[0]
        return {"ads_coin": my_waller.current_balance}, "Thóc hiện tại", status.HTTP_200_OK


class AppotaWebhookAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            app = AppotaService()
            data = request.data.get("data")
            signature = request.data.get("signature")

            re_sig = app.generate_signature(data)

            decode_data = decode_result_data(data)
            order_id = decode_data['partnerReference']['order']['id']

            data_check_order = app.get_order(order_id)
            status_code = data_check_order['transaction']['status']
            transaction = Transaction.objects.get(id=order_id)
            transaction.add_appota_response(decode_data)
            if status_code == 'success':
                transaction.update_deposit_status('00')
                my_wallet = Wallet.objects.get_or_create(user=transaction.from_user)[0]
                my_wallet.add_balance(int(transaction.information_detail['item_data']['coin_price']))
                send_and_save_notification(user=transaction.from_user,
                                           title='Giao dịch nạp thóc thành công',
                                           body=f"Số dư thóc hiện tại: {my_wallet.current_balance}",
                                           custom_data={
                                               'direct_type': 'DEPOSIT_SUCCESS'
                                           })

            return Response({'status': 'ok'}, status=status.HTTP_200_OK)
        except Exception as e:
            logging(e)
            return {}, "Lỗi thanh toán", status.HTTP_400_BAD_REQUEST

    @api_decorator
    def get(self, request):
        app = AppotaService()
        data = request.query_params.get("data")
        signature = request.query_params.get("signature")

        re_sig = app.generate_signature(data)

        decode_data = decode_result_data(data)

        order_id = decode_data['partnerReference']['order']['id']

        data_check_order = app.get_order(order_id)
        status_code = data_check_order['transaction']['status']
        transaction = Transaction.objects.get(id=order_id)
        transaction.add_appota_response(decode_data)
        if status_code == 'error':
            transaction.update_deposit_status('01')
            send_and_save_notification(user=transaction.from_user,
                                       title='Thông báo',
                                       body='Giao dịch nạp thóc thất bại',
                                       custom_data={
                                           'direct_type': 'DEPOSIT_FAIL'
                                       })
        time.sleep(20)
        return {}, "Ok", status.HTTP_200_OK


class BankInformationAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        banks = Banking.objects.all().order_by('fullname')
        serializer = MBBankInfoSerializer(banks, context={"request": request}, many=True)
        return serializer.data, "Danh sách ngân hàng", status.HTTP_200_OK


class GetListVipToBuyAPIView(APIView):
    permission_classes = [AllowAny, ]

    @api_decorator
    def get(self, request):
        banks = Vip.objects.all().order_by('total_month')
        serializer = VipSerializer(banks, context={"request": request}, many=True)
        return serializer.data, "Danh sách vip", status.HTTP_200_OK


class BuyVipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request, pk):
        vip = Vip.objects.get(id=pk)

        wallet = Wallet.objects.get_or_create(user=request.user)[0]
        if wallet.current_balance < vip.coin_price:
            return {}, "Không đủ thóc", status.HTTP_400_BAD_REQUEST

        trans = Transaction.objects.create(from_user=request.user,
                                           funds='Coin',
                                           transaction_type='vip',
                                           amount=vip.coin_price,
                                           return_code='00'
                                           )
        data_trade = VipSerializer(vip).data
        trans.add_detail("vip", data_trade)
        wallet.subtract_balance(vip.coin_price)
        send_and_save_notification(user=request.user,
                                   title='Mua vip thành công',
                                   body=f"Số dư thóc hiện tại: {wallet.current_balance}",
                                   direct_type='BUY_VIP_SUCCESS')

        user_vip = UserVip.objects.get_or_create(user=request.user)[0]
        now = timezone.now()
        if user_vip.date_start is None or user_vip.date_end < now:
            user_vip.date_start = now
            user_vip.date_end = now + datetime.timedelta(days=vip.total_month * 30)
        else:
            user_vip.date_end += timezone.timedelta(days=vip.total_month * 30)

        user_vip.vip = vip
        user_vip.save()

        VIPLog.objects.create(user=request.user,
                              vip=data_trade)

        # Schedule reminder task 3 days before expiration
        reminder_time = user_vip.date_end - timezone.timedelta(days=3)
        send_vip_expiration_reminder.s(str(request.user.id)).apply_async(eta=reminder_time)

        # Schedule reset settings task at expiration
        reset_vip_settings.s(str(request.user.id)).apply_async(eta=user_vip.date_end)

        return {
            'is_vip': True,
            'coin': wallet.current_balance
        }, "Mua vip thành công", status.HTTP_200_OK


class GetCurrentVipAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        user_vip = UserVip.objects.get_or_create(user=request.user)[0]
        if user_vip.vip is not None:
            serializer = UserVipSerializer(user_vip)
            return serializer.data, "Gói vip hiện tại", status.HTTP_200_OK
        else:
            return None, "Bạn chưa mua vip", status.HTTP_200_OK


class GetHistoryVipBuyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        user_vip = VIPLog.objects.filter(user=request.user).select_related('user').order_by('-created_at')
        qs, paginator = get_paginator_limit_offset(user_vip, request)
        data = paginator.get_paginated_response(VipLogSerializer(qs, many=True).data).data
        return data, "Lịch sử mua vip", status.HTTP_200_OK
