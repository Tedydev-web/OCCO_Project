import os
import django
import uuid
import random
import requests
from io import BytesIO
from django.core.files import File
from PIL import Image
from django.core.management import BaseCommand
from faker import Faker

from apps.general.management.fake_data.images import HOT_BOY_IMAGE_URLS, HOT_GIRL_IMAGE_URLS
from apps.user.models import *
from apps.general.models import FileUpload

# Đặt các thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

fake = Faker('vi_VN')


# Hàm để tải ảnh từ URL
def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    return None


# Hàm để tạo số điện thoại với tiền tố +84
def generate_vietnam_phone_number():
    return '+84' + fake.msisdn()[2:]


# Hàm để lưu ảnh vào FileUpload
def save_image_to_file_upload(image, user, file_type='IMAGE'):
    temp_file = BytesIO()
    image.save(temp_file, format=image.format)
    temp_file.seek(0)
    file_upload = FileUpload(
        owner=user,
        file=File(temp_file, name=f"{uuid.uuid4()}.{image.format.lower()}"),
        file_type='IMAGE'
    )
    file_upload.save()
    return file_upload


# Danh sách họ người Việt Nam
VIETNAMESE_LAST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ",
                         "Hồ", "Ngô", "Dương", "Lý", "An", "Bạch", "Bành", "Cao", "Châu", "Chung", "Chử", "Cung",
                         "Danh", "Đinh", "Đoàn", "Đồng", "Đới", "Đồng", "Giang", "Hạ", "Hà", "Hàn", "Kiều", "Kim",
                         "Khoa", "Lâm", "Liễu", "Lu", "Lục", "Lưu", "Lương", "Lý", "Mã", "Mạch", "Mai", "Mạc", "Mạch",
                         "Mai", "Mẫn", "Mông", "Mục", "Mễ", "Nghiêm", "Nghị", "Nhạc", "Phó", "Phùng", "Quách", "Quản",
                         "Quan", "Quản", "Quang", "Quách", "Quận", "Quế", "Quỳnh", "Sầm", "Sử", "Thái", "Thái", "Thân",
                         "Thành", "Thư", "Thực", "Thủy", "Tiêu", "Tiếp", "Tiền", "Tô", "Tôn", "Tôn Thất", "Tống", "Trà",
                         "Trác", "Trang", "Triệu", "Trình", "Trưng", "Trương", "Ung", "Văn", "Vi", "Viên", "Võ",
                         "Võ Văn", "Vương", "Xa", "Xuân", "Yên"]

# Danh sách tên người Việt Nam
VIETNAMESE_NAMES_MALE = ["An", "Bảo", "Cường", "Đạt", "Đức", "Dũng", "Hải", "Hiếu", "Hùng", "Hưng", "Khải", "Linh",
                         "Long", "Minh", "Nam", "Phong", "Phú", "Quân", "Quang", "Sơn", "Tùng", "Tú", "Tuấn", "Việt",
                         "Vinh", "Vũ"]
VIETNAMESE_NAMES_FEMALE = ["Ái", "Anh", "Bích", "Chi", "Diễm", "Dung", "Hà", "Hạnh", "Hương", "Huyền", "Lan", "Linh",
                           "Loan", "Mai", "My", "Nga", "Nhi", "Phương", "Quỳnh", "Thảo", "Thu", "Trâm", "Trang",
                           "Trinh", "Uyên", "Xuân"]


# Hàm để tạo tên theo giới tính
def generate_name_by_gender(gender):
    if gender in ['MALE', 'GAY']:
        return f"{random.choice(VIETNAMESE_LAST_NAMES)} {random.choice(VIETNAMESE_NAMES_MALE)}"
    elif gender == ['FEMALE', 'LESBIAN']:
        return f"{random.choice(VIETNAMESE_LAST_NAMES)} {random.choice(VIETNAMESE_NAMES_FEMALE)}"
    else:
        first_name = random.choice(VIETNAMESE_NAMES_MALE if random.random() < 0.5 else VIETNAMESE_NAMES_FEMALE)
        last_name = random.choice(VIETNAMESE_LAST_NAMES)
        return f"{last_name} {first_name}"


# Hàm để tạo tên theo giới tính
# Danh sách các tỉnh thành trong các vùng miền của Việt Nam
northern_provinces = ['HÀ NỘI', 'LÀO CAI', 'YÊN BÁI', 'ĐIỆN BIÊN', 'LAI CHÂU', 'SƠN LA',
                      'HÀ GIANG', 'CAO BẰNG', 'BẮC KẠN', 'LẠNG SƠN', 'TUYÊN QUANG', 'THÁI NGUYÊN', 'PHÚ THỌ',
                      'BẮC GIANG', 'QUẢNG NINH', 'BẮC NINH', 'HÀ NAM', 'HẢI DƯƠNG', 'HẢI PHÒNG',
                      'HÒA BÌNH', 'HƯNG YÊN', 'NAM ĐỊNH', 'NINH BÌNH', 'THÁI BÌNH', 'VĨNH PHÚC']

central_provinces = ['ĐÀ NẴNG', 'THANH HOÁ', 'NGHỆ AN', 'HÀ TĨNH', 'QUẢNG BÌNH', 'QUẢNG TRỊ',
                     'THỪA THIÊN HUẾ', 'QUẢNG NAM', 'QUẢNG NGÃI', 'BÌNH ĐỊNH', 'PHÚ YÊN', 'KHÁNH HÒA',
                     'NINH THUẬN', 'BÌNH THUẬN', 'KON TUM', 'GIA LAI', 'ĐẮK LẮK', 'ĐẮK NÔNG', 'LÂM ĐỒNG']

southern_provinces = ['HỒ CHÍ MINH', 'CẦN THƠ', 'BÌNH PHƯỚC', 'TÂY NINH', 'BÌNH DƯƠNG', 'ĐỒNG NAI',
                      'BÀ RỊA - VŨNG TÀU', 'LONG AN', 'TIỀN GIANG', 'BẾN TRE', 'TRÀ VINH', 'VĨNH LONG',
                      'ĐỒNG THÁP', 'AN GIANG', 'KIÊN GIANG', 'HẬU GIANG', 'SÓC TRĂNG', 'BẠC LIÊU', 'CÀ MAU']


# Hàm để chọn tỉnh thành ngẫu nhiên từ các vùng miền
def generate_province():
    region = random.choice([northern_provinces, central_provinces, southern_provinces])
    return random.choice(region)


def generate_vietnam_coordinates():
    # Giới hạn về vĩ độ và kinh độ của Việt Nam
    min_lat, max_lat = 8.0, 23.4  # Phạm vi vĩ độ của Việt Nam
    min_lng, max_lng = 102.1, 109.5  # Phạm vi kinh độ của Việt Nam

    # Tạo tọa độ ngẫu nhiên trong phạm vi của Việt Nam
    lat = round(random.uniform(min_lat, max_lat), 6)
    lng = round(random.uniform(min_lng, max_lng), 6)

    return lat, lng

def generate_hcmc_coordinates():
    # Giới hạn về vĩ độ và kinh độ của Hồ Chí Minh City
    min_lat, max_lat = 10.3, 11.2  # Phạm vi vĩ độ của Hồ Chí Minh City
    min_lng, max_lng = 106.4, 107.0  # Phạm vi kinh độ của Hồ Chí Minh City

    # Tạo tọa độ ngẫu nhiên trong phạm vi của Hồ Chí Minh City
    lat = round(random.uniform(min_lat, max_lat), 6)
    lng = round(random.uniform(min_lng, max_lng), 6)

    return lat, lng


class Command(BaseCommand):
    help = 'Delete notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--number',
            type=int,
            help='The number of notifications to delete',
        )

    def handle(self, *args, **kwargs):
        for _ in range(kwargs['number']):
            # Hàm để tạo người dùng ngẫu nhiên
            gender = fake.random_element(elements=['MALE', 'FEMALE', 'GAY', 'LESBIAN'])
            full_name = generate_name_by_gender(gender)
            lat, lng = generate_hcmc_coordinates()
            user = CustomUser.objects.create(
                full_name=full_name,
                bio=fake.text(max_nb_chars=200),
                email=fake.email(),
                phone_number=generate_vietnam_phone_number(),
                date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=30),
                age=fake.random_int(min=18, max=30),
                gender=gender,
                height=fake.random_int(min=150, max=185),
                weight=fake.random_int(min=50, max=80),
                register_status='DONE',
                province=str('HỒ CHÍ MINH').title(),
                lat=lat,
                lng=lng,
                is_fake=True,
                is_online=fake.boolean(),
            )

            # Tải và lưu avatar và cover_image
            if user.gender in ['MALE', 'GAY']:
                avatar_url = random.choice(HOT_BOY_IMAGE_URLS)
                cover_image_url = random.choice(HOT_BOY_IMAGE_URLS)
            else:
                avatar_url = random.choice(HOT_GIRL_IMAGE_URLS)
                cover_image_url = random.choice(HOT_GIRL_IMAGE_URLS)

            avatar_image = download_image(avatar_url)
            cover_image = download_image(cover_image_url)

            if avatar_image:
                avatar_upload = save_image_to_file_upload(avatar_image, user)
                user.avatar = avatar_upload

            if cover_image:
                cover_image_upload = save_image_to_file_upload(cover_image, user)
                user.cover_image = cover_image_upload

            user.save()

            # Tải và lưu nhiều ảnh profile
            for _ in range(random.randint(1, 6)):
                if user.gender in ['MALE', 'GAY']:
                    profile_image_url = random.choice(HOT_BOY_IMAGE_URLS)
                else:
                    profile_image_url = random.choice(HOT_GIRL_IMAGE_URLS)

                profile_image = download_image(profile_image_url)
                if profile_image:
                    profile_image_upload = save_image_to_file_upload(profile_image, user)
                    ProfileImage.objects.create(user=user, image=profile_image_upload)

            # Tạo và liên kết BaseInformation
            base_info = BaseInformation.objects.create(user=user)

            # Lấy các thông tin phụ từ các bảng đã có sẵn và liên kết với BaseInformation
            for model, field in [
                (SearchInformation, base_info.search),
                (WorkInformation, base_info.work),
                (CharacterInformation, base_info.character),
                (HobbyInformation, base_info.hobby),
                (CommunicateInformation, base_info.communicate),
            ]:
                all_objects = list(model.objects.all())
                if all_objects:
                    selected_objects = random.sample(all_objects,
                                                     k=min(len(all_objects), 5))  # Lấy ngẫu nhiên tối đa 5 đối tượng
                    for obj in selected_objects:
                        field.add(obj)

            base_info.save()
            print("Tạo thành công user", user.full_name)
