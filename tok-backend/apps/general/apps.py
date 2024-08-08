from django.apps import AppConfig
from django.core.management import call_command
from django.db.models.signals import post_migrate


class GeneralConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.general'
    has_run = False  # Biến lớp để theo dõi xem command đã chạy hay chưa
    verbose_name = 'Cài đặt và liên hệ'

    #
    def ready(self):
        # Kết nối signal post_migrate với hàm run_on_startup
        from apps.general import signal
        post_migrate.connect(self.run_on_startup, sender=self)

    #
    def run_on_startup(self, sender, **kwargs):
        # Kiểm tra xem command đã được gọi chưa
        if not self.__class__.has_run:
            # Gọi command load_appconfig
            call_command('load_information')
            call_command('load_discovery')
            from apps.user.models import CustomUser

            if not CustomUser.objects.filter(phone_number='+84398765432').exists():
                print('Add superuser successfully')
                CustomUser.objects.create_superuser('+84398765432', password='Cydeva@2024')
            else:
                print('Superuser already exists')

            if not CustomUser.objects.filter(phone_number='+84987654321').exists():
                print('Add superuser successfully')
                qs = CustomUser.objects.create_superuser('+84987654321', password='Cydeva@2024')
                qs.full_name = 'Chăm sóc khách hàng'
                qs.save()
            else:
                print('Superuser already exists')
            # Đặt cờ đã chạy để đảm bảo rằng command chỉ được gọi một lần
            self.__class__.has_run = True
