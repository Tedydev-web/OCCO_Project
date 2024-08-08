# conversation/consumers.py
import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from django_redis import get_redis_connection

from api.services.telegram import logging
from apps.user.models import CustomUser
from apps.user.tasks import remove_private_chat_5_hours_inactive


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    redis_conn = get_redis_connection("default")

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        params = dict(param.split('=') for param in query_string.split('&'))
        user_id = params.get('user_id')

        if not user_id:
            await self.close()
            return

        self.user_id = user_id
        self.room_group_name = f"user_{user_id}"

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

        try:
            user = await self.get_user(user_id)
            print(user)
        except CustomUser.DoesNotExist:
            await self.close()
            return

        user =await self.set_user_online(user)

        await self.add_user_to_redis()

        await self.update_connected_users()

    async def disconnect(self, close_code):
        user_id = self.user_id

        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

        try:
            user = await self.get_user(user_id)
            # logging(user)
        except CustomUser.DoesNotExist:
            return

        await self.remove_user_from_redis(user)

        user = await self.update_user_online_status(user)
        await self.remove_private_chat(self.user_id)
        await self.update_connected_users()

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "user.message", "message": message}
        )

    async def user_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps(message, ensure_ascii=False))

    async def update_connected_users(self):
        all_users = await self.get_all_connected_users()
        for user_id in all_users:
            room_group_name = f"user_{user_id}"
            await self.channel_layer.group_send(
                room_group_name,
                {"type": "user.update_connected_users", "connected_users": all_users}
            )

    async def user_update_connected_users(self, event):
        connected_users_list = event["connected_users"]

        await self.send(text_data=json.dumps({"connected_users": connected_users_list}, ensure_ascii=False))

    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def remove_private_chat(self, user_id):
        remove_private_chat_5_hours_inactive.s(user_id).apply_async(countdown=0)

    @database_sync_to_async
    def set_user_online(self, user):
        user.set_online(True)
        return user
    @database_sync_to_async
    def remove_user_from_redis(self, user):
        self.redis_conn.srem(f"user_{user.id}_channels", self.channel_name)
        if self.redis_conn.scard(f"user_{user.id}_channels") == 0:
            self.redis_conn.delete(f"user_{user.id}_channels")

    @database_sync_to_async
    def update_user_online_status(self, user):
        user.set_online(False)
        return user

    @database_sync_to_async
    def get_all_connected_users(self):
        return [key.decode().split('_')[1] for key in self.redis_conn.keys('user_*_channels')]

    async def add_user_to_redis(self):
        self.redis_conn.sadd(f"user_{self.user_id}_channels", self.channel_name)
