from django.urls import path
from .views import *

urlpatterns = [
    path('buy-coin/', BuyCoinAPIView.as_view()),
    path('buy/list-coin/', ListCoinBuyAPIView.as_view()),
    path('withdraw/list-coin/', ListMoneyTradingAPIView.as_view()),
    path('my-coin/', CurrentCoinAPIView.as_view()),
    path('buy-gift/<uuid:pk>/', BuyGiftAPIView.as_view()),
    path('trade-gift/', TradeGiftToCoinAPIView.as_view()),
    path('withdraw-coin/', WithdrawCoinAPIView.as_view()),
    path('history/transaction/coin/', HistoryTransactionCoinAPIView.as_view()),
    path('send-gift/', SendGiftToUserAPIView.as_view()),

    path('history/gift-send/', HistoryTransactionGiftAPIView.as_view()),

    path('list-uid/', ListUIDAPIView.as_view()),
    path('buy-uid/<uuid:pk>/', BuyUIDAPIView.as_view()),
    path('buy-avatar-frame/<uuid:pk>/', BuyAvatarFrameAPIView.as_view()),
    path('trade/ads-wallet/', TradeCoinToAdsWalletAPIView.as_view()),
    path('appota/returnURL/', AppotaWebhookAPIView.as_view()),

    path('list-bank/', BankInformationAPIView.as_view()),

    path('list-vip/', GetListVipToBuyAPIView.as_view()),
    path('buy-vip/<uuid:pk>/', BuyVipAPIView.as_view()),
    path('current-vip/', GetCurrentVipAPIView.as_view()),
    path('history/vip-buy/', GetHistoryVipBuyAPIView.as_view()),

]
