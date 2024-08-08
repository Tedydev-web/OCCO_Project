# celery.py

import os

import django
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# Define a custom beat scheduler with modifications

celery_app = Celery('core')

# load task modules from all registered Django app configs.
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
# autodiscover tasks in all installed apps

celery_app.autodiscover_tasks()

# Optional: Debugging output
print(f"Celery Timezone: {celery_app.conf.timezone}")
print(f"Celery Enable UTC: {celery_app.conf.enable_utc}")
