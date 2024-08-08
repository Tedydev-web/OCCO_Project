import io
import json

from PIL import Image, ExifTags
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import uuid

from api.services.google_map import get_address
from api.services.nsfw_validator import nsfw_image_validator
from apps.dashboard.models import NotificationAdmin
from apps.general.models import FileUpload, DevSetting, Sticker, StickerCategory, AvatarFrame, AppInformation
from apps.general.serializers import FileUploadSerializer, GetFileUploadSerializer, ReportSerializer, \
    FeedBackSerializer, StickerSerializer, StickerCategorySerializer, AvatarFrameSerializer
from apps.general.models import FileUpload, DevSetting, CoinTrading, AboutUs
from apps.general.serializers import FileUploadSerializer, GetFileUploadSerializer, ReportSerializer, \
    FeedBackSerializer, CoinTradingSerializer
from apps.user.models import CustomUser
from ultis.api_helper import api_decorator
from ultis.file_helper import get_video_dimensions, get_video_duration, mime_to_file_type, get_audio_duration
from api.services.telegram_admin import send_telegram_message


class FileUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        file = request.FILES.get('file')
        file_type = mime_to_file_type(file.name)
        max_file_size_bytes = 1024 * 1024  # 1MB

        if file_type == 'IMAGE':
            file = self.compress_image(file, max_file_size_bytes)
            nsfw_image_validator(file)
            request.data['file'] = file

        if file_type == 'VIDEO':
            try:
                if isinstance(file, InMemoryUploadedFile):
                    file_content = io.BytesIO(file.read())  # Use BytesIO for in-memory files
                else:
                    file_content = open(file.temporary_file_path(), 'rb')  # Use file path for larger files

                # Process video dimensions and duration
                video_width, video_height = get_video_dimensions(file_content)
                file_duration = int(get_video_duration(file_content))

                request.data['video_width'] = video_width
                request.data['video_height'] = video_height
                request.data['file_duration'] = file_duration

            except Exception as e:
                print(f"Error processing video file: {str(e)}")

        if file_type == 'AUDIO':
            try:
                if isinstance(file, InMemoryUploadedFile):
                    file_content = io.BytesIO(file.read())  # Use BytesIO for in-memory files
                else:
                    file_content = open(file.temporary_file_path(), 'rb')  # Use file path for larger files

                # Process audio duration
                request.data['file_duration'] = int(get_audio_duration(file_content))

            except Exception as e:
                print(f"Error processing audio file: {str(e)}")

        request.data['owner'] = str(request.user.id)
        request.data['file_type'] = file_type
        serializer = FileUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()

        return serializer.data, 'Upload successful!', status.HTTP_201_CREATED

    def compress_image(self, file, max_size):
        img = Image.open(file)

        # Correct orientation using EXIF data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                orientation = exif.get(orientation, 1)
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # If there is an issue with EXIF data, ignore and proceed
            pass

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')

        # Save image to BytesIO with initial quality
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=90)
        output_size = output.tell()

        # Resize image if the output size exceeds the maximum size
        while output_size > max_size:
            img = img.resize((int(img.size[0] * 0.9), int(img.size[1] * 0.9)), Image.LANCZOS)
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=90)
            output_size = output.tell()

        output.seek(0)
        return InMemoryUploadedFile(output, None, file.name, 'image/jpeg', output_size, None)


class FileUploadsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        files = request.data.getlist('files')
        max_file_size_bytes = 1024 * 1024  # 1MB
        list_file = []
        for file in files:
            file_type = mime_to_file_type(file.name)
            if file_type == 'IMAGE':
                # file = self.compress_image(file, max_file_size_bytes)
                nsfw_image_validator(file)
                request.data['file'] = file

            if file_type == 'VIDEO':
                try:
                    if isinstance(file, InMemoryUploadedFile):
                        file_content = io.BytesIO(file.read())  # Use BytesIO for in-memory files
                    else:
                        file_content = open(file.temporary_file_path(), 'rb')  # Use file path for larger files

                    # Process video dimensions and duration
                    video_width, video_height = get_video_dimensions(file_content)
                    file_duration = int(get_video_duration(file_content))

                    request.data['video_width'] = video_width
                    request.data['video_height'] = video_height
                    request.data['file_duration'] = file_duration

                except Exception as e:
                    print(f"Error processing video file: {str(e)}")

            if file_type == 'AUDIO':
                try:
                    if isinstance(file, InMemoryUploadedFile):
                        file_content = io.BytesIO(file.read())  # Use BytesIO for in-memory files
                    else:
                        file_content = open(file.temporary_file_path(), 'rb')  # Use file path for larger files

                    # Process audio duration
                    request.data['file_duration'] = int(get_audio_duration(file_content))

                except Exception as e:
                    print(f"Error processing audio file: {str(e)}")

            request.data['owner'] = str(request.user.id)
            request.data['file_type'] = file_type
            serializer = FileUploadSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
            list_file.append(serializer.data)
        return list_file, "Danh sách các file", status.HTTP_201_CREATED

    def compress_image(self, file, max_size):
        img = Image.open(file)

        # Correct orientation using EXIF data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = img._getexif()
            if exif is not None:
                orientation = exif.get(orientation, 1)
                if orientation == 3:
                    img = img.rotate(180, expand=True)
                elif orientation == 6:
                    img = img.rotate(270, expand=True)
                elif orientation == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # If there is an issue with EXIF data, ignore and proceed
            pass

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P', 'LA'):
            img = img.convert('RGB')

        # Save image to BytesIO with initial quality
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=90)
        output_size = output.tell()

        # Resize image if the output size exceeds the maximum size
        while output_size > max_size:
            img = img.resize((int(img.size[0] * 0.9), int(img.size[1] * 0.9)), Image.LANCZOS)
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=90)
            output_size = output.tell()

        output.seek(0)
        return InMemoryUploadedFile(output, None, file.name, 'image/jpeg', output_size, None)


class GetFileUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def get(self, request):
        queryset = FileUpload.objects.filter(owner=request.user)
        serializer = GetFileUploadSerializer(queryset, many=True, context={'request': request})
        return serializer.data, 'Retrieve data successfully!', status.HTTP_200_OK


class FileUploadByIDAPIView(APIView):

    @api_decorator
    def get(self, request, pk):
        queryset = FileUpload.objects.filter(owner_id=pk)
        serializer = GetFileUploadSerializer(queryset, many=True, context={'request': request})
        return serializer.data, 'Retrieve data successfully!', status.HTTP_200_OK


class GetDevSettingAPIView(APIView):
    @api_decorator
    def get(self, request):
        return DevSetting.objects.get(pk=1).config, "Settings for dev", status.HTTP_200_OK


class GetPhoneNumbersAPIView(APIView):
    @api_decorator
    def get(self, request):
        with open('constants/country.json', encoding='utf-8') as file:
            data = json.load(file)
            return data, "Country for dev", status.HTTP_200_OK


class ReportAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        # report = Report.objects.create()
        request.data['user'] = request.user.id

        serializer = ReportSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        data = serializer.data
        url_admin = f"https://occo.tokvn.live/admin/general/report/{data['id']}/change/"
        notification_admin = NotificationAdmin.objects.create(
            from_user=request.user,
            title=f"{request.user.full_name} vừa tố cáo {CustomUser.objects.get(id=data['direct_user']).full_name}",
            body=f"với lý do: {data['content']}",
            type='REPORT',
            link=url_admin
        )
        send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)

        return data, 'Tố cáo thành công!', status.HTTP_200_OK


class FeedBackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @api_decorator
    def post(self, request):
        request.data['sender'] = request.user.id
        serializer = FeedBackSerializer(data=request.data, context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()

        data = serializer.data
        url_admin = f"https://occo.tokvn.live/admin/general/feedback/{data['id']}/change/"

        notification_admin = NotificationAdmin.objects.create(
            from_user=request.user,
            title=f"{request.user.full_name} vừa phản ánh {data['full_name']}",
            body=f"với lý do: {data['description']}",
            type='REFLECT',
            link=url_admin
        )

        send_telegram_message.s(notification_admin=str(notification_admin.id)).apply_async(countdown=1)
        return data, 'Phản hồi thành công!', status.HTTP_200_OK


class GetAboutUsAPIView(APIView):
    @api_decorator
    def get(self, request):
        qs = AboutUs.objects.first()
        return qs.description, "Hướng dẫn", status.HTTP_200_OK


class ListStickerCategoryAPIView(APIView):
    @api_decorator
    def get(self, request):
        qs = StickerCategory.objects.filter(is_active=True).order_by('index')
        serializer = StickerCategorySerializer(qs, many=True)
        return serializer.data, "Danh sách bộ nhãn", status.HTTP_200_OK


class ListStickerAPIView(APIView):
    @api_decorator
    def get(self, request):
        sticker_category_id = request.query_params.get('sticker_category_id', None)
        if sticker_category_id:
            qs = Sticker.objects.filter(sticker_category__id=sticker_category_id,
                                        is_active=True).order_by('index')
        else:
            qs = Sticker.objects.filter(is_active=True).order_by('index')

        serializer = StickerSerializer(qs, many=True)
        return serializer.data, "Danh sách sticker", status.HTTP_200_OK


class ListAvatarFrameAPIView(APIView):
    @api_decorator
    def get(self, request):
        qs = AvatarFrame.objects.filter(is_active=True).order_by('-coin_price')
        serializer = AvatarFrameSerializer(qs, many=True)
        return serializer.data, "Danh sách khung avt", status.HTTP_200_OK


class GetAddressFromLatLngAPIView(APIView):
    permission_classes = [IsAuthenticated, ]

    @api_decorator
    def post(self, request):
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        address = get_address(lat, lng)
        return address, "Địa chỉ từ lat lng", status.HTTP_200_OK


class GetAppInformationAPIView(APIView):

    @api_decorator
    def get(self, request):
        keyword = request.query_params.get('keyword', None)
        app_info = AppInformation.objects.get(key=keyword)
        return app_info.value, f"Thông tin {app_info.title}", status.HTTP_200_OK
