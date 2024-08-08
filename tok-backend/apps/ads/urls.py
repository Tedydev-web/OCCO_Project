from django.urls import path

from apps.ads.views import *

urlpatterns = [
    # Owner
    path('owner/list/', ListOwnerAdsAPIView.as_view()),
    path('owner/create/', CreateAdsAPIView.as_view()),
    path('owner/update/<uuid:pk>/', UpdateAdsAPIView.as_view()),
    path('owner/delete/<uuid:pk>/', DeleteAdsAPIView.as_view()),
    path('detail/<uuid:pk>/', DetailAdsAPIView.as_view()),

    # Target
    path('user/list/', GetListAdsForUserAPIView.as_view()),
    path('user/view/<uuid:pk>/', ViewAdsAPIView.as_view()),
    path('user/click/<uuid:pk>/', ClickAdsAPIView.as_view()),
]
