from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db.models import Q, Sum, IntegerField

from api.services.telegram import logging
from apps.general.models import FileUpload
from ultis.file_helper import format_file_size


class Command(BaseCommand):
    help = 'Delete unnecessary file'

    def handle(self, *args, **options):
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            # Lọc các đối tượng FileUpload không nằm trong danh sách và thời gian tạo nhỏ hơn 1 giờ trước
            qs = FileUpload.objects.filter(Q(blog=None) &
                                           Q(owner=None) &
                                           Q(report=None) &
                                           Q(room=None) &
                                           Q(message=None) &
                                           Q(livestreamhistory=None) &
                                           Q(created_at__lt=one_hour_ago))
            try:
                file_sizes = [file_obj.file.size for file_obj in qs]

                # Tính tổng kích thước của tất cả các tệp
                total_size = sum(file_sizes)
            except:
                total_size = 0
            # Thực hiện xóa các đối tượng không được tham chiếu
            count_deleted, _ = qs.delete()
            if count_deleted != 0:
                logging(f'{datetime.now().strftime("%H:%M %d/%m/%Y")} Auto deleted {count_deleted} unreferenced files.'
                        f'\nTotal: {format_file_size(total_size)}')
                self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count_deleted} unreferenced files.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error deleting unnecessary files: {str(e)}'))
