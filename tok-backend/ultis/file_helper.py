import mimetypes
import os
import uuid
from io import BytesIO
from tempfile import NamedTemporaryFile

from django.template.defaultfilters import filesizeformat
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip


def format_file_size(size_in_bytes):
    max_size = 1 * 1024 * 1024 * 1024  # 1GB
    # if size_in_bytes > max_size:
    #     raise ValidationError("File size cannot exceed 1GB.")
    return filesizeformat(size_in_bytes)


def custom_media_file_path(instance, filename, path):
    owner_id = str(instance.owner.id)
    upload_path = os.path.join(f'user_media/{owner_id}/', path)
    new_filename = f'{uuid.uuid4()}{os.path.splitext(filename)[1]}'
    return os.path.join(upload_path, new_filename)


def get_video_dimensions(file_path):
    try:
        clip = VideoFileClip(file_path)
        width = clip.size[0]
        height = clip.size[1]
        clip.close()
        return width, height
    except Exception as e:
        print(f"Error: {e}")
        return None, None


def get_video_duration(file_path):
    try:
        clip = VideoFileClip(file_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_audio_duration(file):
    # Đọc dữ liệu của file âm thanh từ đối tượng InMemoryUploadedFile
    audio_data = file.read()

    # Lưu dữ liệu vào một tệp tạm thời
    temp_file = NamedTemporaryFile(delete=False, suffix='.mp3')
    temp_file.write(audio_data)
    temp_file.close()

    # Tạo đối tượng AudioFileClip từ tệp tạm thời
    audio_clip = AudioFileClip(temp_file.name)

    # Lấy độ dài của file âm thanh trong giây
    duration_in_seconds = audio_clip.duration
    audio_clip.close()
    # Xóa tệp tạm thời sau khi sử dụng xong
    os.unlink(temp_file.name)

    return duration_in_seconds


def mime_to_file_type(file_name):
    mime_type, _ = mimetypes.guess_type(file_name)
    if mime_type is not None:
        if mime_type.startswith('image'):
            return 'IMAGE'
        elif mime_type.startswith('video'):
            return 'VIDEO'
        elif mime_type == 'application/pdf':
            return 'PDF'
        elif mime_type.startswith('audio'):
            return 'AUDIO'
    return 'UNKNOWN'
