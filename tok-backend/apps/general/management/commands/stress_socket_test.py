import asyncio

import websockets
from asgiref.sync import sync_to_async
from django.core.management import BaseCommand

from apps.user.models import CustomUser


class Command(BaseCommand):
    help = 'Load stress test socket'
    user_counter = 1
    def handle(self, *args, **options):

        asyncio.run(self.stress_test_sockets())

    async def stress_test_sockets(self):
        users = await sync_to_async(list)(CustomUser.objects.filter(is_fake=True)[:500])
        tasks = []
        for user in users:
            tasks.append(self.connect_user(user.id))
        await asyncio.gather(*tasks)

    async def connect_user(self, user_id):
        try:
            uri = f"ws://localhost:8006/user/online/?user_id={user_id}"
            async with websockets.connect(uri) as websocket:
                print(f"User {user_id} (#{self.user_counter}) connected")  # Print user ID and order
                self.user_counter += 1  # Increment the user counter
                await asyncio.sleep(60)  # Keep the connection open for 1 minute
                print(f"User {user_id} disconnecting")
        except Exception as e:
            print(f"Error for user {user_id}: {e}")
        finally:
            await self.ensure_disconnect(user_id)

    async def ensure_disconnect(self, user_id):
        try:
            uri = f"ws://localhost:8006/user/online/?user_id={user_id}"
            async with websockets.connect(uri) as websocket:
                await websocket.close()
        except Exception as e:
            print(f"Ensure disconnect error for user {user_id}: {e}")