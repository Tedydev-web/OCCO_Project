from django.urls import path
from apps.discovery.views import *

urlpatterns = [
    #   =========================  Host LiveStreaming ==========================
    path("host/create/", HostCreateLiveStreamAPIView.as_view()),
    path("host/update/<uuid:pk>/", HostUpdateLiveStreamAPIView.as_view()),
    path("host/delete/<uuid:pk>/", HostRemoveLiveStreamAPIView.as_view()),
    path("host/kick/user-join/", HostKickUserAPIView.as_view()),
    path("host/choose/key/", HostChooseUserToKeyAPIView.as_view()),
    path("host/remove/key/", HostChooseUserToMemberAPIView.as_view()),
    path("host/list/", ListMyLiveStreamAPIView.as_view()),
    path("host/kick/user-chair/", HostKickUserChairAPIView.as_view()),
    path("host/stop-live/<uuid:pk>/", HostStopLiveAPIView.as_view()),

    #   == =======================  List LiveStreaming ==========================
    path("chat/list/", GetListLiveChatAPIView.as_view()),
    path("voice/list/", GetListLiveVoiceAPIView.as_view()),
    path("video/list/", GetListLiveVideoAPIView.as_view()),
    path("stream/list/", GetListLiveStreamAPIView.as_view()),
    path("list-viewer/<uuid:pk>/", GetListViewerAPIView.as_view()),

    path("search/", SearchLiveByKeywordAPIView.as_view()),
    path("search/live/", SearchLiveStreamByKeywordAPIView.as_view()),

    #   =========================  User LiveStreaming ==========================
    path("user/join/live/<uuid:pk>/", UserJoinLiveStreamAPIView.as_view()),
    path("user/leave/live/<uuid:pk>/", UserLeaveLiveStreamAPIView.as_view()),

    path("user/join/chair/<uuid:pk>/", UserJoinChairStreamAPIView.as_view()),
    path("user/leave/chair/<uuid:pk>/", UserLeaveChairStreamAPIView.as_view()),
    path("user/recently/list/", UserRecentlyJoinLiveStreamAPIView.as_view()),

    #   =========================  In Live ==========================
    path("gift/list/", GetListGiftChatAPIView.as_view()),
    path("emoji/list/", GetListEmojiChatAPIView.as_view()),
    path("user/send-msg/<uuid:pk>/", SendMessageToLiveAPIView.as_view()),
    path("user/send-gift/<uuid:pk>/", SendGiftToLiveAPIView.as_view()),
    path("user/send-emoji/<uuid:pk>/", SendEmojiToLiveAPIView.as_view()),
    path("detail/message/<uuid:pk>/", HistoryMsgOfLiveAPIView.as_view()),

    path("detail/chairs/<uuid:pk>/", HistoryChairsOfLiveAPIView.as_view()),
    path("detail/live/<uuid:pk>/", DetailLiveAPIView.as_view()),

    path('chairs/micro/<uuid:pk>/', OnOffMicroAPIView.as_view())

]
