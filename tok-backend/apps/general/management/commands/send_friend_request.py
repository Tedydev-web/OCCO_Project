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
            receiver = CustomUser.objects.get(id='dcf02cf2-3d59-494c-b93d-9611f7784788')
            users_fake = CustomUser.objects.filter(is_fake=True)
            users_fake = random.sample(list(users_fake), 10)
            # Lấy một đối tượng ngẫu nhiên từ queryset users_fake

            request_factory = RequestFactory()
            request = request_factory.get('/')

            for sender in users_fake:
                request.user = sender

                follow, created = Follow.objects.get_or_create(from_user=request.user, to_user=receiver)

                if created:
                    receiver.add_follower(sender.id)

                    request.user.add_following(receiver.id)

                queryset = FriendShip.objects.filter(Q(sender=request.user, receiver_id=receiver.id) |
                                                     Q(sender_id=receiver.id, receiver=request.user))
                check_friend_ship = queryset.exists()

                if check_friend_ship:  # đã từng gửi yêu cầu nhưng bị hủy kết bạn hoặc từ chối sẽ vào case này
                    friend_ship = queryset[0]

                    if friend_ship.status == 'PENDING':
                        pass

                    elif friend_ship.status == 'ACCEPTED':
                        pass
                    else:
                        friend_ship.status = 'PENDING'
                        friend_ship.save()
                        send_noti_add_friend(request.user, receiver)
                        self.stdout.write(self.style.SUCCESS(f'Send friend to {receiver.full_name} from {sender.full_name}'))
                else:
                    friend_ship = FriendShip.objects.create(sender=request.user, receiver_id=receiver.id)
                    send_noti_add_friend(request.user, receiver)
                    self.stdout.write(self.style.SUCCESS(f'Send friend to {receiver.full_name} from {sender.full_name}'))

                time.sleep(3)

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending fake message: {str(e)}'))
