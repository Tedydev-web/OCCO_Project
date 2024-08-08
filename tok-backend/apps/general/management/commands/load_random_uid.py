import random
import string
from django.core.management.base import BaseCommand

from apps.general.models import UIDTrading


def generate_unique_uid():
    return ''.join(random.choices(string.digits, k=8))


def generate_beautiful_uid():
    beautiful_uids = [
        '88888888', '99999999', '77777777', '44444444', '12345678', '66666666', '111111111', '22222222', '98765432', '00000000', '33333333',
        '55555555', '34567890'
    ]
    return random.choice(beautiful_uids)


def determine_coin_price(uid):
    high_value_uids = [
        '88888888', '99999999', '77777777', '44444444', '12345678', '66666666', '111111111', '22222222', '98765432', '00000000', '33333333',
        '55555555', '34567890'
    ]
    if uid in high_value_uids:
        return random.randint(500, 4000)  # Giá cao hơn cho các UID đặc biệt
    return random.randint(1, 50)  # Giá thông thường cho các UID khác


class Command(BaseCommand):
    help = 'Generate 30 unique UIDs and save to the database'

    def handle(self, *args, **options):
        try:
            for _ in range(30):
                if random.random() < 0.5:  # 20% cơ hội tạo ra một số đẹp
                    uid = generate_beautiful_uid()
                    while UIDTrading.objects.filter(uid=uid).exists():
                        uid = generate_beautiful_uid()
                else:
                    uid = generate_unique_uid()
                    while UIDTrading.objects.filter(uid=uid).exists():
                        uid = generate_unique_uid()

                coin_price = determine_coin_price(uid)

                UIDTrading.objects.create(uid=uid, coin_price=coin_price)

            self.stdout.write(self.style.SUCCESS('Successfully generated 30 UIDs'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error generating UIDs: {str(e)}"))