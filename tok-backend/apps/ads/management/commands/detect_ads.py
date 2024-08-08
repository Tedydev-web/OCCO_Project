import json
import os
import requests
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Q, Sum, IntegerField

from api.services.telegram import logging
from apps.ads.models import Advertisement
from apps.notification.models import Notification


class Command(BaseCommand):
    help = 'Detect ads'

    def handle(self, *args, **options):
        try:
            now = datetime.now().date()
            ads_incoming = Advertisement.objects.filter(start_date=now, status_verify='verified',
                                                        status_coming='incoming')
            for ad in ads_incoming:
                ad.change_status_coming()
            if ads_incoming:
                logging(f"{str(now)} Detected ads incoming: {ads_incoming.count()}")

            ads_expired = Advertisement.objects.filter(end_date__lt=now).exclude(status_coming='expired').exclude(status_verify='rejected')
            for ad in ads_expired:
                ad.change_status_expired()
            if ads_expired:
                logging(f"{str(now)} Detected ads expired: {ads_expired.count()}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error detect advertisement: {str(e)}'))
            logging(f'Error detect advertisement: {str(e)}')
