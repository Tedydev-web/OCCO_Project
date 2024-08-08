import logging
from pathlib import Path
import os

from django.utils import timezone
from dotenv import load_dotenv
from typing import Any, Dict
from django.utils.translation import gettext_lazy as _

from core.jazzmin import JAZZMIN_SETTINGS_, JAZZMIN_UI_TWEAKS_

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')[:-1]

CSRF_TRUSTED_ORIGINS = [
    'https://tok.cydeva.tech',
    'https://bucket.cydeva.tech',
    'https://occo.cydevaltd.com',
    'https://uat.occo.nphdigital.online',
    'http://localhost:9000',
    'https://occo.tokvn.live'
]

INSTALLED_APPS = [
    "daphne",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.postgres',
    "django_celery_beat",
    "apps.user",
    "apps.general",
    "apps.conversation",
    "apps.discovery",
    "apps.notification",
    'apps.blog',
    'apps.friend',
    'apps.webhook',
    "rest_framework",
    "storages",
    'ckeditor_uploader',
    'ckeditor',
    'django.contrib.humanize',
    'celery',
    'corsheaders',
    'channels',
    'django_admin_inline_paginator',
    'silk',
    'nplusone.ext.django',
    'dbbackup',
    'apps.dashboard',
    'apps.payment',
    'apps.ads',
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.user.auth.JWTAuthentication",
        'rest_framework.authentication.SessionAuthentication',
    ],
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    'django.middleware.locale.LocaleMiddleware',
    'nplusone.ext.django.NPlusOneMiddleware',
    'silk.middleware.SilkyMiddleware',  # track and profiling API
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = "core.urls"
LOGIN_REDIRECT_URL = '/'
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                'django.template.context_processors.static',
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = 'core.asgi.application'
AUTH_USER_MODEL = 'user.CustomUser'
# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
USE_DB = os.getenv('USE_DB') == 'True'

if USE_DB:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASS'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': os.environ.get('DB_PORT'),
            'OPTIONS': {
                'options': '-c timezone=Asia/Ho_Chi_Minh',
            },
        }
    }

else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': 'backup'}

REDIS_LOCAL = os.getenv('REDIS_LOCAL') == 'True'
if REDIS_LOCAL:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": ["redis://127.0.0.1:6379/1"],
                "capacity": 500,  # Increase this value as needed
            },
        },
    }
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/4",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "TIMEOUT": 60,
            }
        }
    }
    CELERY_BROKER_URL = 'redis://127.0.0.1:6379/2'
    CELERY_RESULT_BACKEND = "redis://127.0.0.1:6379/3"
else:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [
                    os.environ.get('SOCKET_REDIS_URL')],
                "capacity": 10000,
            },
        },
    }
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.environ.get('CACHE_REDIS_URL'),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "TIMEOUT": 600,
            }
        }
    }
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"
# DJANGO_REDIS_IGNORE_EXCEPTIONS = True

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'vi'

LANGUAGES = [
    ('vi', _('Vietnamese')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale/')
]

USE_TZ = True
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_L10N = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'staticfiles'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CKEDITOR_UPLOAD_PATH = "uploads/"

CKEDITOR_CONFIGS = {
    'default': {
        'versionCheck': False,
        'toolbar': 'Custom',
        'width': '100%',
        'toolbar_Custom': [
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline',
             'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['Smiley', 'SpecialChar'], ['Source'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['NumberedList', 'BulletedList'],
            ['Indent', 'Outdent'],
            ['Maximize'],
        ],
        'autoParagraph': False,
        'enterMode': 2,
    }
}

JAZZMIN_SETTINGS = JAZZMIN_SETTINGS_
JAZZMIN_UI_TWEAKS = JAZZMIN_UI_TWEAKS_

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'  # Explicitly set this to None
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

if os.getenv('USE_MINIO') == 'True':
    STORAGES = {
        "default": {"BACKEND": 'storages.backends.s3boto3.S3Boto3Storage'},
        "staticfiles": {"BACKEND": 'storages.backends.s3boto3.S3Boto3Storage'},
    }

    AWS_ACCESS_KEY_ID = os.getenv("MINIO_ROOT_USER")
    AWS_SECRET_ACCESS_KEY = os.getenv("MINIO_ROOT_PASSWORD")
    AWS_STORAGE_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT")
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False

OTP_PROVIDER_ID = os.getenv('OTP_PROVIDER_ID')
ZALO_OTP_URL = os.getenv('ZALO_OTP_URL')

STRINGEE_APP_ID = os.getenv("STRINGEE_APP_ID")
STRINGEE_APP_SECRET = os.getenv("STRINGEE_APP_SECRET")

SILKY_PYTHON_PROFILER = True
SILKY_AUTHENTICATION = True  # User must login
SILKY_AUTHORISATION = True  # User must have permissions
SILKY_META = True
SILKY_HIDE_SENSITIVE = False

SILKY_EXPLAIN_FLAGS = {'format': 'JSON', 'costs': True}
# If this is not set, MEDIA_ROOT will be used.

NPLUSONE_LOGGER = logging.getLogger('nplusone')
NPLUSONE_LOG_LEVEL = logging.WARN
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'nplusone': {
            'handlers': ['console'],
            'level': 'WARN',
        },
    },
}
NPLUSONE_WHITELIST = [
    {"model": "admin.LogEntry", "field": "user"},
    {"model": "apps.CustomUser", "field": "groups"},
    {"model": "apps.CustomUser", "field": "user_permissions"},
]

DATETIME_FORMAT = "d/m/Y H:m"
DATE_FORMAT = "d/m/Y"

AGORA_APP_CERTIFICATE = os.getenv("AGORA_APP_CERTIFICATE")
AGORA_APP_ID = os.getenv("AGORA_APP_ID")


CELERY_BEAT_SCHEDULE = {
    'send-vip-expiration-reminders': {
        'task': 'apps.payment.tasks.check_and_send_vip_expiration_reminders',
        'schedule': timezone.timedelta(hours=24),  # Run once a day
    },
    'reset-vip-settings': {
        'task': 'apps.payment.check_and_reset_vip_settings',
        'schedule': timezone.timedelta(hours=24),  # Run once a day
    },
}