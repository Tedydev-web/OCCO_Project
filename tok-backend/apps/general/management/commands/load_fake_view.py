import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread

from django.core.management import BaseCommand

from apps.discovery.models import LiveUser, LiveStreamingHistory
from apps.user.models import CustomUser


class Command(BaseCommand):
    help = 'Delete notifications'

    def handle(self, *args, **kwargs):
        fake_users = list(CustomUser.objects.filter(is_fake=True))
        lives = LiveStreamingHistory.objects.all()

        max_workers = 10  # Adjust this number based on your server's capacity
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for live in lives:
                num_users_fake = random.randint(1, 25)  # Random number of fake users for each live
                users_fake = random.sample(fake_users, num_users_fake)  # Randomly select fake users
                for user in users_fake:
                    futures.append(executor.submit(self.process_live_user, live, user))

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.stderr.write(str(e))

    def process_live_user(self, live, user):
        try:
            live_user, created = LiveUser.objects.get_or_create(user=user, live_streaming=live)
            if created:
                live_user.set_role('USER')

            # Change online in room
            live_user.join_room()
            # Add user to live
            live.add_view(live_user)

            print(f"Join {live} - user:{user}")
        except Exception as e:
            self.stderr.write(f"Error processing {live} - user:{user}: {e}")
