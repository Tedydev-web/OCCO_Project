# conversation/consumers.py
import asyncio
import datetime
import json
import random
import time
from itertools import chain

from channels.db import database_sync_to_async
from django.db.models import Q
from django.test import RequestFactory

from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer

from api.services.telegram import logging
from apps.conversation.models import Room, PrivateQueue, RoomUser, RandomQueue
from apps.conversation.serializers import RoomSerializer
from apps.general.models import DevSetting
from apps.user.models import CustomUser
from ultis.socket_helper import send_to_socket, get_socket_data


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope['query_string'].decode()
        params = dict(param.split('=') for param in query_string.split('&'))
        room_id = params.get('user_id')

        if not room_id:
            await self.close()
            return

        self.room_id = room_id
        self.room_group_name = f"conversation_{room_id}"

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
            self.room_group_name, {"type": "conversation.message", "message": message}
        )

    async def conversation_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message, ensure_ascii=False))


class PrivateChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.closed = False
        self.disconnect_event = asyncio.Event()
        self.tasks = []

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        params = dict(param.split('=') for param in query_string.split('&'))
        user_id = params.get('user_id')
        self.room_group_name = f"private_{user_id}"
        self.user_id = user_id
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

        self.start_time = time.time()
        self.closed = False
        self.disconnect_event.clear()

        # Create asyncio tasks for the main operation and periodic checks
        self.tasks.append(asyncio.create_task(self.main_operation(user_id)))
        self.tasks.append(asyncio.create_task(self.check_timeout()))

    async def main_operation(self, user_id):
        try:
            while not self.closed:
                user = await self.get_user(user_id)
                request_factory = RequestFactory()
                request = request_factory.get('/')
                request.user = user
                if self.disconnect_event.is_set():
                    await self.close()
                    break

                room, other = await self.create_private_room(user)
                if room is not None:
                    logging(f"Tạo phòng ẩn danh giữa: {user.full_name} - {other.full_name} - {str(room.id)}")
                    await self.delete_private_queue(other)
                    data = await self.get_room_serializer(room, request)
                    self.closed = True
                    await self.send(
                        text_data=json.dumps(get_socket_data('NEW_ROOM', data=data), ensure_ascii=False))
                    await self.close()

                if self.disconnect_event.is_set():
                    await self.close()
                    break

        except Exception as e:
            print("Exception in main operation: %s", e)
        finally:
            self.closed = True
            self.disconnect_event.set()

    async def check_timeout(self):
        while not self.closed:
            if time.time() - self.start_time > await self.get_time_queue():
                await self.delete_user_from_queue(self.user_id)
                await self.send(
                    text_data=json.dumps(get_socket_data('TIME_OUT', data={}), ensure_ascii=False)
                )
                self.closed = True
                await self.close()
                break
            await asyncio.sleep(1)
            if self.disconnect_event.is_set():
                break

    async def disconnect(self, close_code):
        try:
            user_id = self.user_id
            print("Attempting to disconnect and delete user: %s", user_id)
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
            await self.delete_user_from_queue(user_id)
            print("Successfully disconnected and deleted user: %s", user_id)
        except Exception as e:
            print("Error during disconnect: %s", e)
        finally:
            self.closed = True
            self.disconnect_event.set()
            for task in self.tasks:
                task.cancel()
            # logging(f"Người dùng {self.user_id} đã thoát khỏi tìm kiếm ẩn danh.")

    async def close(self, code=None):
        # logging("Connection is closing with code: %s", code)
        await super().close(code)
        self.disconnect_event.set()
        for task in self.tasks:
            task.cancel()

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "private.message", "message": message}
            )
        except Exception as e:
            print(f"Exception during receive: {e}")

    async def private_message(self, event):
        try:
            message = event["message"]

            # Send message to WebSocket
            await self.send(text_data=json.dumps({"message": message}, ensure_ascii=False))
        except Exception as e:
            print(f"Exception during private_message: {e}")

    async def close(self, code=None):
        await super().close(code)
        self.closed = True
        self.stop = True
        self.disconnect_event.set()

    @database_sync_to_async
    def get_room_serializer(self, room, request):
        return RoomSerializer(room, context={'request': request}).data

    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def join_private_queue(self, user):
        return PrivateQueue.objects.get_or_create(user=user)

    @database_sync_to_async
    def delete_private_queue(self, user):
        try:
            PrivateQueue.objects.filter(user=user).delete()
        except:
            print(user)

    @database_sync_to_async
    def create_private_room(self, user):
        room = Room.objects.create(type='PRIVATE')
        other = CustomUser.custom_objects.filter_blocked_users(user).filter(is_fake=False, is_online=True).exclude(
            id=user.id)
        if len(other) == 0:
            return None, None
        other = random.sample(list(other), 1)[0]
        RoomUser.objects.bulk_create([
            RoomUser(room=room, user=user),
            RoomUser(room=room, user=other)
        ])
        return room, other

    @database_sync_to_async
    def delete_user_from_queue(self, user_id):
        qs = PrivateQueue.objects.filter(user__id=user_id).delete()
        print(qs)
        return qs

    @database_sync_to_async
    def get_time_queue(self):
        return DevSetting.get_time_queue()


class RandomChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.closed = False
        self.disconnect_event = asyncio.Event()
        self.tasks = []

    async def connect(self):
        query_string = self.scope['query_string'].decode()
        params = dict(param.split('=') for param in query_string.split('&'))
        user_id = params.get('user_id')
        self.room_group_name = f"random_{user_id}"
        self.user_id = user_id
        self.closed = False
        self.disconnect_event.clear()

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

        self.start_time = time.time()

        # Create asyncio tasks for the main operation and timeout check
        self.tasks.append(asyncio.create_task(self.main_operation(user_id)))
        self.tasks.append(asyncio.create_task(self.check_timeout()))

    async def main_operation(self, user_id):
        try:
            while not self.closed:
                user = await self.get_user(user_id)
                request_factory = RequestFactory()
                request = request_factory.get('/')
                request.user = user

                recommended_users = await self.get_recommended_users(user)
                is_random_filter = await self.get_random_filter()
                # print(is_random_filter)
                if self.disconnect_event.is_set():
                    await self.close()
                    break
                # Check if user is in a random room

                # print("Đang tìm kiếm người ngẫu nhiên: %s", user)
                # room = await self.get_unused_random_room(user)
                # print("Step 1 find room: %s", str(room))
                # if room is not None:
                #     await self.set_room_used_and_connect(room)
                #     print("Found random room:", room)
                #
                #     logging(f"User đang trong phòng ngẫu nhiên: {user.full_name} - {str(room.id)}")
                #
                #     data = await self.get_room_serializer(room, request)
                #     await self.send(
                #         text_data=json.dumps(get_socket_data('NEW_ROOM', data=data), ensure_ascii=False)
                #     )
                #     self.closed = True
                #     await self.close()
                #     break
                #
                # if self.disconnect_event.is_set():
                #     await self.close()
                #     break
                # Join the queue here
                print("Step 1 join queue")
                user_join = await self.join_random_queue(user)
                if user_join.is_stop:
                    await self.delete_random_queue(user)
                    self.closed = True
                    await self.close()
                    break
                # Finding other in queue
                print("Step 2 find other user")
                other = await self.get_other_in_queue(user, recommended_users, is_random_filter)
                print("Step 3 if other")
                if other:
                    room = await self.create_random_room(user, other)
                    await self.set_room_used_and_connect(room)
                    logging(f"Đã tìm thấy phòng ngẫu nhiên: {str(room.id)} - {user.full_name} - {other.full_name}")
                    await self.delete_random_queue(user)
                    await self.delete_random_queue(other)

                    data = await self.get_room_serializer(room, request)
                    await self.send(
                        text_data=json.dumps(get_socket_data('NEW_ROOM', data=data), ensure_ascii=False)
                    )
                    await self.send_other_found_room(other, data)
                    self.closed = True
                    await self.close()
                    break

                if self.disconnect_event.is_set():
                    await self.close()
                    break

        except Exception as e:
            print("Exception in main operation: %s", e)
        finally:
            self.closed = True
            self.disconnect_event.set()

    async def check_timeout(self):
        while not self.closed:
            if time.time() - self.start_time > await self.get_time_queue():
                await self.delete_user_from_queue(self.user_id)
                await self.send(
                    text_data=json.dumps(get_socket_data('TIME_OUT', data={}), ensure_ascii=False)
                )
                self.closed = True
                await self.close()
                break
            await asyncio.sleep(1)
            if self.disconnect_event.is_set():
                break

    async def send_other_found_room(self, other, data):
        send_to_socket("random", str(other.id), get_socket_data('NEW_ROOM', data=data))

    async def disconnect(self, close_code):
        try:
            user_id = self.user_id
            print("Attempting to disconnect and delete user: %s", user_id)
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
            await self.delete_user_from_queue(user_id)
            print("Successfully disconnected and deleted user: %s", user_id)
        except Exception as e:
            print("Error during disconnect: %s", e)
        finally:
            self.closed = True
            self.disconnect_event.set()
            for task in self.tasks:
                task.cancel()
            # logging(f"Người dùng {self.user_id} đã thoát khỏi tìm kiếm ngẫu nhiên.")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "random.message", "message": message}
            )
        except Exception as e:
            print("Exception during receive: %s", e)

    async def close(self, code=None):
        # logging("Connection is closing with code: %s", code)
        await super().close(code)
        self.disconnect_event.set()
        for task in self.tasks:
            task.cancel()

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "random.message", "message": message}
            )
        except Exception as e:
            print(f"Exception during receive: {e}")

    async def random_message(self, event):
        try:
            message = event["message"]

            # Send message to WebSocket
            await self.send(text_data=json.dumps({"message": message}, ensure_ascii=False))
        except Exception as e:
            print(f"Exception during random_message: {e}")

    @database_sync_to_async
    def get_time_queue(self):
        return DevSetting.get_time_queue()

    @database_sync_to_async
    def get_room_serializer(self, room, request):
        return RoomSerializer(room, context={'request': request}).data

    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def get_recommended_users(self, user):
        if DevSetting.get_value('random_filter') in {'true', True}:
            return CustomUser.custom_objects.recommend_users(user).values_list('id', flat=True)
        else:
            return CustomUser.custom_objects.filter_blocked_users(user).values_list('id', flat=True)

    @database_sync_to_async
    def get_random_filter(self):
        return DevSetting.get_value('random_filter') in {'true', True}

    @database_sync_to_async
    def get_unused_random_room(self, user):
        return Room.objects.filter(type='RANDOM', roomuser__user=user, is_used=False).first()

    @database_sync_to_async
    def set_room_used_and_connect(self, room):
        room.set_used()
        room.set_connect()

    @database_sync_to_async
    def join_random_queue(self, user):
        return RandomQueue.objects.get_or_create(user=user)[0]

    @database_sync_to_async
    def delete_random_queue(self, user):
        try:
            RandomQueue.objects.filter(user=user).delete()
        except Exception as e:
            print(e, user)

    @database_sync_to_async
    def get_other_in_queue(self, user, recommended_users, is_random_filter):
        try:
            if not is_random_filter:
                print(is_random_filter)
                blocked = CustomUser.custom_objects.list_blocking(user)
                return RandomQueue.objects.exclude(
                    user__id__in=blocked).exclude(user=user).first().user
            else:
                return RandomQueue.objects.filter(user__id__in=recommended_users).exclude(user=user).first().user()
        except Exception as e:
            print(e)
            return None

    @database_sync_to_async
    def create_random_room(self, user1, user2):
        room = Room.objects.filter(
            Q(roomuser__user=user1) &
            (Q(type='CONNECT') | Q(type='RANDOM'))).filter(
            Q(roomuser__user=user2)
        ).first()
        if room:
            return room

        room = Room.objects.create(type='RANDOM')
        RoomUser.objects.bulk_create([
            RoomUser(room=room, user=user1),
            RoomUser(room=room, user=user2)
        ])
        return room

    @database_sync_to_async
    def delete_user_from_queue(self, user_id):
        try:
            RandomQueue.objects.filter(user__id=user_id).delete()
        except:
            ...
