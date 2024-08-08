from django.urls import path

from apps.general.views import *

urlpatterns = [
    path('upload/', FileUploadAPIView.as_view()),
    path('upload-multi/', FileUploadsAPIView.as_view()),
    path('upload/user/', GetFileUploadAPIView.as_view()),
    path('upload/user/<uuid:pk>/', FileUploadByIDAPIView.as_view()),

    path('dev-setting/', GetDevSettingAPIView.as_view()),
    path('country/', GetPhoneNumbersAPIView.as_view()),

    path('report/', ReportAPIView.as_view()),
    path('feedback/', FeedBackAPIView.as_view()),
    path('about-us/', GetAboutUsAPIView.as_view()),

    path('sticker/', ListStickerAPIView.as_view()),
    path('sticker/category/', ListStickerCategoryAPIView.as_view()),

    path('get-address/', GetAddressFromLatLngAPIView.as_view()),

    path('avatar-frame/', ListAvatarFrameAPIView.as_view()),
    path('app-information/', GetAppInformationAPIView.as_view()),
]
