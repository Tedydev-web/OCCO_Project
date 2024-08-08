from django.urls import path
from .views import *

urlpatterns = [
    # =======================  Friend =============================

    path('list/<uuid:pk>/', ListFriendShipAPIView.as_view()),

    path('requests/list/', RequestFriendShipAPIView.as_view()),

    path('add/', AddFriendShipAPIView.as_view()),
    path('accept/user/', AcceptFriendByUserIDAPIView.as_view()),
    path('reject/user/', RejectFriendByUserIDAPIView.as_view()),
    path('delete/user/', DeleteFriendByUserIDAPIView.as_view()),
    path('revoke/user/', RevokeRequestFriendByUserID.as_view()),

    path('check/', IsFriendAPIView.as_view()),

    # =======================  Recommended =============================
    path('recommended/', FriendCommendedAPIView.as_view()),
    path('nearby/', FriendNearbyAPIView.as_view()),
    # =======================  Match =============================

    path('match/', FriendMatchAPIView.as_view()),
    # =======================  find =============================

    path('find/', FindUserByFullName.as_view()),

]
