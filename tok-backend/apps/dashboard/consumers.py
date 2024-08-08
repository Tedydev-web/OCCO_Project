import json

from channels.generic.websocket import AsyncWebsocketConsumer

from api.services.telegram import logging


class AdminSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        params = dict(param.split('=') for param in query_string.split('&'))
        room_id = params.get('user_id')

        if not room_id:
            await self.close()
            return

        self.room_id = room_id
        self.room_group_name = f"admin_{room_id}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "admin.message", "message": message}
        )

    async def admin_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message, ensure_ascii=False))