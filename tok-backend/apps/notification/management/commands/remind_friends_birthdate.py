import datetime
from django.core.management.base import BaseCommand

from api.services.firebase import send_and_save_notification
from apps.user.models import CustomUser


class Command(BaseCommand):
    help = 'Remind friends birthdate'

    def handle(self, *args, **options):
        try:
            today = datetime.datetime.today().day
            month = datetime.datetime.today().month
            all_birthdate_today = CustomUser.objects.filter(date_of_birth__day=today,date_of_birth__month=month)
            for user in all_birthdate_today:
                msg = f"Hôm nay {today}/{month} là sinh nhật của {user.full_name}, hãy gửi một lời chúc tốt đẹp nhé!"
                list_friends = CustomUser.custom_objects.list_friend(user)
                for friend in list_friends:
                    if user != friend:
                        send_and_save_notification(user=friend,
                                                   body=msg,
                                                   direct_user=user,
                                                   type_noti='FRIEND')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error remind friend birthdate notifications: {str(e)}'))