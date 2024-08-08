from celery import shared_task
from django.core.management import call_command


@shared_task
def detect_advertisement():
    call_command("detect_ads")
