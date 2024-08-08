import random
import time

from django.core.management import BaseCommand
from django.db.models import Q
from django.test import RequestFactory

from apps.user.models import CustomUser, FriendShip, Follow
from apps.user.serializers import FriendShipSerializer
from ultis.socket_friend_helper import send_noti_add_friend


class Command(BaseCommand):
    help = 'Send friend request'

    def handle(self, *args, **options):
        try:
            # receivers = CustomUser.objects.filter(is_fake=False, is_superuser= False)
            receivers = CustomUser.objects.filter(id='dcf02cf2-3d59-494c-b93d-9611f7784788')
            users_fake = CustomUser.objects.filter(is_fake=True)
            users_fake = random.sample(list(users_fake), 5)
            # Lấy một đối tượng ngẫu nhiên từ queryset users_fake

            request_factory = RequestFactory()
            request = request_factory.get('/')
            for receiver in receivers:
                for sender in users_fake:
                    request.user = sender

                    follow, created = Follow.objects.get_or_create(from_user=request.user, to_user=receiver)

                    if created:
                        receiver.add_follower(sender.id)
                        request.user.add_following(receiver.id)

                    queryset = FriendShip.objects.filter((Q(sender=request.user, receiver_id=receiver.id) |
                                                          Q(sender_id=receiver.id, receiver=request.user)),
                                                         status='ACCEPTED').first()

                    if queryset:  # đã từng gửi yêu cầu nhưng bị hủy kết bạn hoặc từ chối sẽ vào case này
                        pass
                    else:
                        friend_ship = FriendShip.objects.create(sender=sender,
                                                                receiver=receiver,
                                                                status='ACCEPTED')

                        friend_ship.sender.plus_count_friend(receiver.id)
                        friend_ship.receiver.plus_count_friend(sender.id)

                        send_noti_add_friend(request.user, receiver)
                        self.stdout.write(
                            self.style.SUCCESS(f'Make friend between {receiver.full_name} and {sender.full_name}'))


        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending fake message: {str(e)}'))
