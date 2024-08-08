from django.core.management import call_command
from celery import shared_task


@shared_task
def remind_birthdate():
    call_command('remind_friends_birthdate',)
