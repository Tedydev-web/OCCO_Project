import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from apps.discovery.task import disconnect_live


class DiscoveryConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        params = dict(param.split('=') for param in query_string.split('&'))
        room_name = params.get('user_id')
        self.user_id = room_name
        self.room_group_name = f"discovery_{self.user_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.user_offline_discovery(self.user_id)
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )
        await self.close()

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "discovery.message", "message": message}
        )

    # Receive message from room group
    async def discovery_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message, ensure_ascii=False))

    @database_sync_to_async
    def user_offline_discovery(self, user_id):
        disconnect_live.s(user_id).apply_async(countdown=0)
