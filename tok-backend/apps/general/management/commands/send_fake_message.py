import random

from django.core.management import BaseCommand
from django.db.models import Q
from django.test import RequestFactory
from apps.conversation.models import Message, Room, RoomUser
from apps.conversation.serializers import MessageSerializer, RoomSerializer, LastMessageSerializer
from apps.general.management.fake_data.messages import MSG
from apps.user.models import CustomUser
from ultis.socket_helper import send_to_socket, get_socket_data, send_noti_to_socket_user, get_socket_data_conversation


class Command(BaseCommand):
    help = 'Send fake message'

    def handle(self, *args, **options):
        try:
            users_real = CustomUser.objects.filter(is_fake=False,is_superuser=False)
            users_fake = CustomUser.objects.filter(is_fake=True)
            # Lấy một đối tượng ngẫu nhiên từ queryset users_fake
            random_user = users_fake.order_by('?').first()
            sender = random_user

            request_factory = RequestFactory()
            request = request_factory.get('/')
            request.user = sender

            for user in users_real:
                msg = random.choices(MSG)[0]
                try:
                    receiver = user
                    room = Room.objects.filter(
                        Q(roomuser__user=receiver) &
                        Q(type='CONNECT')).filter(
                        Q(roomuser__user=sender)
                    ).first()

                    if not room:
                        room = Room.objects.create(type='CONNECT')
                        room_users = RoomUser.objects.bulk_create([
                            RoomUser(room=room, user=sender),
                            RoomUser(room=room, user=receiver)
                        ])

                    room.set_newest()

                    msg = Message.objects.create(sender=sender,
                                                 type='TEXT',
                                                 room=room,
                                                 text=msg
                                                 )

                    serializer_msg = MessageSerializer(msg, context={'request':request})
                    data_msg = serializer_msg.data

                    rs = room.roomuser_set.all()
                    rs.update(date_removed=None)
                    serializer_room = RoomSerializer(room, context={'request': request})
                    data_room = serializer_room.data
                    last_msg = data_msg

                    data_room['last_message'] = last_msg

                    for r in rs:
                        if r.user != sender:
                            r.set_total_unseen()
                        # Set last message to enhance performance
                        r.set_last_message(last_msg)

                        send_to_socket('conversation', str(r.user.id),
                                       get_socket_data_conversation('NEW_MESSAGE', data_msg, room_id=str(room.id)))
                        send_to_socket('conversation', str(r.user.id),
                                       get_socket_data_conversation('NEW_CONVERSATION', data_room,
                                                                    room_id=str(room.id)))
                    # Tạo một đối tượng HttpRequest giả mạo


                    self.stdout.write(self.style.SUCCESS(f'Send {msg.text} to {receiver.full_name}'))
                except Exception as e:
                    print(e)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending fake message: {str(e)}'))