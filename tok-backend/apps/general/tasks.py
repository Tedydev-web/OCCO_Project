from celery import shared_task
from django.core.management import call_command


@shared_task
def delete_unnecessary_file():
    call_command('delete_unnecessary_file', )


@shared_task
def delete_notification():
    call_command('delete_notification', )


@shared_task
def detect_advertisement():
    call_command("detect_ads")


@shared_task
def detect_video_call_live():
    call_command("detect_video_call_live")