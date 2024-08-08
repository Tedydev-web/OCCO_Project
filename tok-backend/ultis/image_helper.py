import uuid
from PIL import Image
from io import BytesIO
import os


def resize_image(image, size=(800, 800)):
    img = Image.open(image)
    img.thumbnail(size)
    output = BytesIO()
    img.save(output, format='JPEG')

    return output


def convert_to_jpeg(image):
    img = Image.open(image)

    output = BytesIO()
    img.convert('RGB').save(output, format='JPEG')
    output.seek(0)

    return output


def compress_image(image, quality):
    img = Image.open(image)
    output = BytesIO()
    img.save(output, format='JPEG', quality=quality)
    return output


def output_compress_image(image, quality, output):
    byte = compress_image(image, quality)
    image = Image.open(byte)
    image.save(output)
    byte.close()
    return output