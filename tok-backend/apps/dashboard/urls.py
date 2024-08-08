from django.urls import path

from apps.dashboard.dashboard import admin_site
from apps.dashboard.views import CSKHView, SearchUserConversationAPIView, GetListRoomChatOfUserAPIView, user_map, \
    GetUIDAPIView, statistics_view

urlpatterns = [
    path('', admin_site.dashboard_view, name='admin_dashboard'),
    path('user-map/', user_map, name='user_map'),
    path('cskh/', CSKHView, name='cskh'),
    path('cskh/search-room/', SearchUserConversationAPIView.as_view()),
    path('cskh/list-room/', GetListRoomChatOfUserAPIView.as_view()),
    path('uid/', GetUIDAPIView.as_view()),
    path('statistics/', statistics_view, name='statistics'),
]