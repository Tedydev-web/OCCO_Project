from django.urls import path
from .views import *

urlpatterns = [
    path('check/exist/', CheckExistUserAPIView.as_view()),

    path('register/', CreateUserAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('login/social/', SocialLoginAPIView.as_view()),

    path('verify/otp/', VerifyOTPAPIView.as_view()),

    path('info/<uuid:pk>/', UserDetailAPIView.as_view()),
    path('update/', UpdateUserAPIView.as_view()),
    path('update/password/', UpdatePasswordAPIView.as_view()),
    path('change/password/', ChangePasswordAPIView.as_view()),

    path('forgot/password/', ForgotPasswordAPIView.as_view()),

    path('base/information/', GetBaseInformationAPIView.as_view()),
    path('base/information/update/', BaseInformationAPIView.as_view()),

    path('update/location/', UpdateLatLngAPIView.as_view()),
    path('location/<uuid:pk>/', GetLocationAPIView.as_view()),

    # ========================= Block ==============================
    path('block/<uuid:pk>/', BlockUserAPIView.as_view()),
    path('unblock/<uuid:pk>/', UnBlockUserAPIView.as_view()),
    path('block/list/', GetBlockUserAPIView.as_view()),
    # ========================= Get token Stringee ==============================
    path('get-token/stringee/', GetStringeeUserAPIView.as_view()),

    # ========================= Follow ===========================
    path('follow/', FollowUserAPIView.as_view()),
    path('unfollow/', UnFollowUserAPIView.as_view()),
    path('following/<uuid:pk>/', ListFollowingUserAPIView.as_view()),  # danh sách người mà pk đang follow
    path('follower/<uuid:pk>/', ListFollowerUserAPI.as_view()),

    # ========================= Delete ===========================
    path('delete/account/', DeleteUserAPIView.as_view()),

    # ======================= CSKH ===========================
    path('cskh/', CSKHAPIView.as_view()),

    # ======================  Private Account =================
    path('update/private/', UpdatePrivateAccountAPIView.as_view()),
    path('update/vip/', UpdateVipAccountAPIView.as_view()),
    path('update/id-card/', UpdateIdCardAPIView.as_view()),
    path('current/id-card/', CurrentIdCardAPIView.as_view()),

    # ======================  Current Account =================
    path('my-gift/', CurrentGiftAPIView.as_view()),
    path('update/notification/', UpdateNotificationAPIView.as_view()),

    # =================== Admin ==================
    path('user-timeline/<uuid:user_id>/', userTimeline, name='userTimeline'),

    path('time-line/',UserTimeLineAPIView.as_view()),

    # ====================== Add=====================
    path('history-seen/',GetHistorySeenPageAPIView.as_view())
]
