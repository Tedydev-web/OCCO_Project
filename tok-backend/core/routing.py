# conversation/routing.py
from django.urls import re_path

from apps.conversation.consumers import ChatConsumer, PrivateChatConsumer, RandomChatConsumer
from apps.dashboard.consumers import AdminSocketConsumer
from apps.discovery.consumers import DiscoveryConsumer
from apps.user.consumers import OnlineStatusConsumer

websocket_urlpatterns = [
    re_path(r"conversation/$", ChatConsumer.as_asgi()),
    re_path(r"private/$", PrivateChatConsumer.as_asgi()),
    re_path(r"random/$", RandomChatConsumer.as_asgi()),
    re_path(r"discovery/$", DiscoveryConsumer.as_asgi()),
    re_path(r"user/online/$", OnlineStatusConsumer.as_asgi()),
    re_path(r"admin/notification/$", AdminSocketConsumer.as_asgi()),
]
