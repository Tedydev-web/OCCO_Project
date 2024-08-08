import os

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.discovery.models import LiveStreamingHistory
from apps.general.models import DevSetting, AppConfig, DefaultAvatar, FileUpload
from apps.user.models import CustomUser

from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Load discovery model'

    def handle(self, *args, **options):
        try:
            northern_provinces = ['HÀ NỘI', 'LÀO CAI', 'YÊN BÁI', 'ĐIỆN BIÊN', 'LAI CHÂU', 'SƠN LA',
                                  'HÀ GIANG',
                                  'CAO BẰNG', 'BẮC KẠN', 'LẠNG SƠN', 'TUYÊN QUANG', 'THÁI NGUYÊN', 'PHÚ THỌ',
                                  'BẮC GIANG', 'QUẢNG NINH', 'BẮC NINH', 'HÀ NAM', 'HẢI DƯƠNG', 'HẢI PHÒNG',
                                  'HÒA BÌNH', 'HƯNG YÊN', 'NAM ĐỊNH', 'NINH BÌNH', 'THÁI BÌNH', 'VĨNH PHÚC']

            central_provinces = ['ĐÀ NẴNG', 'THANH HOÁ', 'NGHỆ AN', 'HÀ TĨNH', 'QUẢNG BÌNH', 'QUẢNG TRỊ',
                                 'THỪA THIÊN HUẾ',
                                 'QUẢNG NAM', 'QUẢNG NGÃI', 'BÌNH ĐỊNH', 'PHÚ YÊN', 'KHÁNH HÒA',
                                 'NINH THUẬN', 'BÌNH THUẬN', 'KON TUM', 'GIA LAI', 'ĐẮK LẮK', 'ĐẮK NÔNG', 'LÂM ĐỒNG']

            southern_provinces = ['TP HỒ CHÍ MINH', 'CẦN THƠ', 'BÌNH PHƯỚC', 'TÂY NINH', 'BÌNH DƯƠNG', 'ĐỒNG NAI',
                                  'BÀ RỊA - VŨNG TÀU',
                                  'LONG AN', 'TIỀN GIANG', 'BẾN TRE', 'TRÀ VINH', 'VĨNH LONG',
                                  'ĐỒNG THÁP', 'AN GIANG', 'KIÊN GIANG', 'HẬU GIANG', 'SÓC TRĂNG',
                                  'BẠC LIÊU', 'CÀ MAU']

            province_groups = {
                'NORTH': northern_provinces,
                'CENTRAL': central_provinces,
                'SOUTH': southern_provinces
            }

            for side, provinces in province_groups.items():
                for province in provinces:
                    if not LiveStreamingHistory.objects.filter(province=province).exists():
                        # Tìm kiếm và tải ảnh từ trang web Google Images
                        search_term = f'ảnh chụp cảnh nổi tiếng ở {province} chất lượng HD'
                        url = f"https://www.google.com/search?q={search_term}&tbm=isch&tbs=isz:l"
                        response = requests.get(url)

                        # Kiểm tra xem yêu cầu có thành công hay không
                        if response.status_code == 200:
                            # Sử dụng BeautifulSoup để phân tích HTML của trang tìm kiếm
                            soup = BeautifulSoup(response.text, 'html.parser')

                            # Tìm tất cả các thẻ <img> chứa ảnh
                            image_tags = soup.find_all('img')

                            # Lấy URL của ảnh đầu tiên
                            for img_tag in image_tags:
                                image_url = img_tag.get('src')

                                # Kiểm tra xem URL có bắt đầu bằng "http://" hoặc "https://" không
                                if image_url and image_url.startswith(('http://', 'https://')):
                                    # Tải ảnh về và lưu vào trường file của mô hình FileUpload
                                    image_response = requests.get(image_url)
                                    if image_response.status_code == 200:
                                        file_content = ContentFile(image_response.content)
                                        # Tạo một FileUpload mới và tải ảnh về
                                        file_upload = FileUpload.objects.create(
                                            owner=CustomUser.objects.get(phone_number='+84398765432'),
                                            file_name=f'{province}.jpg',
                                            file_type='IMAGE'
                                        )
                                        file_upload.file.save(name=f'{province}.jpg', content=file_content)
                                        # Lưu URL của ảnh vào trường cover_image của mô hình LiveStreamingHistory
                                        live, created = LiveStreamingHistory.objects.get_or_create(
                                            province=province,
                                            type='CHAT',
                                            side=side,
                                            country='VI',
                                            name=province,
                                            title=f'Phòng chat chung cho người {province.title()}'
                                        )
                                        live.cover_image = file_upload
                                        live.save()
                                        print(f'Success province {province}')

                                        break
                    else:
                        ...

            if not LiveStreamingHistory.objects.filter(country='VI',
                                                       side='ALL').exists():
                file_upload = FileUpload.objects.create(
                    owner=CustomUser.objects.get(phone_number='+84398765432'),
                    file_name=f'vn.jpg',
                    file_type='IMAGE'
                )
                file_upload.file.save('vn', open('constants/default_images/vn.jpg', 'rb'))
                live, created = LiveStreamingHistory.objects.get_or_create(
                    type='CHAT',
                    side='ALL',
                    country='VI',
                    cover_image=file_upload,
                    name='TOÀN QUỐC',
                    title='Phòng chat chung cho người Việt'
                )
                self.stdout.write(self.style.SUCCESS('Default VN room success.'))
            else:
                self.stdout.write(self.style.WARNING('Default VN room already exists.'))
            print("Images downloaded and URLs saved successfully.")

        except Exception as e:
            print(f"Error: {str(e)}")
