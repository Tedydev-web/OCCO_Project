from django.urls import path

from apps.notification.views import UnsubscribeAPIView, SubscribeAPIView, NotiListAPIView, SendPushNotificationAPIView, \
    MarkAllReadAPIView, MarkReadByIdAPIView, SendPushAllNotificationAPIView, CountUnReadNotificationAPIView

urlpatterns = [
    # ----------MOBILE----------

    path('subscribe/', SubscribeAPIView.as_view()),
    path('unsubscribe/', UnsubscribeAPIView.as_view()),

    path('all/', NotiListAPIView.as_view()),
    path('read/mark-all/', MarkAllReadAPIView.as_view()),
    path('read/<uuid:pk>/', MarkReadByIdAPIView.as_view()),

    path('push/', SendPushNotificationAPIView.as_view()),
    path('push/all/', SendPushAllNotificationAPIView.as_view()),

    path('un-read/', CountUnReadNotificationAPIView.as_view()),

    # --------WEB APP--------


]
