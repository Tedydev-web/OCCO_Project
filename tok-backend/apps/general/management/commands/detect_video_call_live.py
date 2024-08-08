from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Q

from api.services.firebase import send_and_save_notification
from api.services.telegram import logging
from apps.discovery.models import LiveStreamingHistory
from apps.notification.models import Notification


class Command(BaseCommand):
    help = 'Delete live 15 days'

    def handle(self, *args, **options):
        try:
            now = datetime.now()
            live_warning = LiveStreamingHistory.objects.filter(type__in=['AUDIO', 'VIDEO']).filter(
                liveuser__role='HOST',
                liveuser__isonline=False,
                last_join__date__gte=now - timedelta(
                    days=7)
            )
            for live in live_warning:
                name = 'VOICE' if live.type == 'AUDIO' else 'VIDEO CALL'
                send_and_save_notification(user=live.host,
                                           title='Thông báo',
                                           body=f'Cảnh báo phòng {name} {live.name} đã không hoạt động 7 ngày, sau 15 ngày hệ thống sẽ tự động xoá!')

            live_delete = LiveStreamingHistory.objects.filter(type__in=['AUDIO', 'VIDEO']).filter(liveuser__role='HOST',
                                                                                                  liveuser__isonline=False,
                                                                                                  last_join__date__gte=now - timedelta(
                                                                                                      days=15)
                                                                                                  )
            for live in live_delete:
                name = 'VOICE' if live.type == 'AUDIO' else 'VIDEO CALL'
                send_and_save_notification(user=live.host,
                                           title='Thông báo',
                                           body=f'Phòng live {name} {live.name} của bạn đã bị xoá do không hoạt động trong 15 ngày')
                live.delete()

        except Exception as e:
            logging(f'Error detect live call and video: {str(e)}')
            self.stdout.write(self.style.ERROR(f'Error deleting notifications: {str(e)}'))
