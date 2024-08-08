from django.urls import path

from apps.webhook.appotapay import AppotaPayAPIView
from apps.webhook.stringee import StringeeAPIView

urlpatterns = [
    path('stringee/', StringeeAPIView.as_view()),
    path('appota-pay/', AppotaPayAPIView.as_view()),
]
