import json
import os
import requests
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Q, Sum, IntegerField

from api.services.telegram import logging
from apps.notification.models import Notification


class Command(BaseCommand):
    help = 'Delete notifications'

    def handle(self, *args, **options):
        try:
            _days_ago = datetime.now() - timedelta(days=30)
            # Lọc các đối tượng FileUpload không nằm trong danh sách và thời gian tạo nhỏ hơn 1 giờ trước
            qs = Notification.objects.filter(Q(created_at__lt=_days_ago))
            # Thực hiện xóa các đối tượng không được tham chiếu
            count_deleted, _ = qs.delete()
            if count_deleted != 0:
                logging(f'{datetime.now().strftime("%H:%M %d/%m/%Y")} Auto deleted {count_deleted} notifications '
                        f'created 30 days ago.')
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count_deleted} notifications'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deleting notifications: {str(e)}'))
