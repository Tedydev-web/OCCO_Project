from django.urls import path

from apps.conversation.admin import room_messages
from apps.conversation.views import *

urlpatterns = [
    #   =========================  Room chat  ==========================
    path('room-user/<uuid:pk>/', CreateRoomOfUserToUseAPIView.as_view()),
    path('list/room/', GetListRoomChatOfUserAPIView.as_view()),
    path('list/online/', GetListOnlineUsersAPIView.as_view()),
    path('detail/room/message/<uuid:pk>/', GetListMessageOfRoomAPIView.as_view()),
    path('detail/room/message-unseen/<uuid:pk>/', GetListMessageUnseenOfRoomAPIView.as_view()),
    path('room/<uuid:pk>/seen/', DetailRoomChatOfUserAPIView.as_view()),

    #   =========================  Chat  ==========================
    path('chat/room/<uuid:pk>/', SendMessageToRoomAPIView.as_view()),
    path('room/<uuid:pk>/mark-unseen/', MarkUnSeenAPIView.as_view()),
    path('room/list/pin-msg/<uuid:pk>/', ListPinMsgOfRoomAPIView.as_view()),
    #   =========================  Call  ==========================
    path('call/room/<uuid:pk>/', CallToRoomAPIView.as_view()),

    path('call/handle/<uuid:pk>/', UserHandleCallAPIView.as_view()),
    #   =========================  Remove, revoke  ==========================
    path('user/remove-room/<uuid:pk>/', UserRemoveRoomAPIView.as_view()),
    path('user/remove-msg/', UserRemoveMessageAPIView.as_view()),
    path('user/revoke-msg/<uuid:pk>/', UserRevokeMessageAPIView.as_view()),
    path('user/edit-msg/<uuid:pk>/', UserEditMessageAPIView.as_view()),
    path('user/pin-msg/<uuid:pk>/', UserPinMessageAPIView.as_view()),
    path('user/unpin-msg/<uuid:pk>/', UserUnPinMessageAPIView.as_view()),

    path('chat/room/update-seen/<uuid:pk>/', UserUpdateSeenMessageAPIView.as_view()),

    #   =========================  Random, Private  ==========================
    path('join/random/chat/', JoinRandomChatAPIView.as_view()),
    path('join/private/chat/', JoinPrivateChatAPIView.as_view()),

    path('leave/random/<uuid:pk>/', LeaveRandomRoomAPIView.as_view()),
    path('leave/private/<uuid:pk>/', LeavePrivateRoomAPIView.as_view()),
    path('stop/queue/', StopQueueAPIView.as_view()),

    #   =========================  Seen, Remove, Block, Report, Search  ==========================
    path('search/user/', SearchUserConversationAPIView.as_view()),
    path('search/room/', SearchRoomAPIView.as_view()),
    path('search/list-recommend/', SearchConversationRecommendAPIView.as_view()),
    path('search/message/', SearchMessageInRoomAPIView.as_view()),
    path('reason/', ReasonAPIView.as_view()),

    #   =========================  Group  ==========================
    path('group/create/', CreateUpdateGroupAPIView.as_view()),
    path('group/update/<uuid:pk>/', CreateUpdateGroupAPIView.as_view()),
    path('group/add/member/', AddMemberToGroupAPIView.as_view()),
    path('group/leave/', LeaveGroupAPIView.as_view()),

    path('group/choose/host/leave/', ChooseHostToLeaveAPIView.as_view()),
    path('group/choose/host/', ChooseNewHostAPIView.as_view()),
    path('group/choose/key/', ChooseMemberToKeyAPIView.as_view()),
    path('group/remove/key/', RemoveMemberFromKeyAPIView.as_view()),

    path('group/remove/user/', RemoveMemberAPIView.as_view()),
    path('group/remove/group/<uuid:pk>/', RemoveGroupAPIView.as_view()),

    path('room/list-users/<uuid:pk>/', ListUserInRoomAPIView.as_view()),

    #   =========================  Recall Msg  ==========================
    path('message/recall/<uuid:pk>/', RemoveMemberAPIView.as_view()),

    #   =========================  Relate  ==========================
    path('background/list-color/', ListBackGroundColorAPIView.as_view()),
    path('room/background/update/<uuid:pk>/', UpdateBackGroundAPIView.as_view()),

    # ====================== Notification, Block, Unblock Room ==================
    path('room/notification/update/', UpdateNotificationModeInRoomAPIView.as_view()),
    path('room/block/<uuid:pk>/', BlockRoom2UserAPIView.as_view()),
    path('room/unblock/<uuid:pk>/', UnBlockRoom2UserAPIView.as_view()),

    # ======================== Admin ===================
    path('room/<uuid:room_id>/messages/', room_messages, name='room_messages'),
]
