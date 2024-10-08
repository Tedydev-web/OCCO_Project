# Generated by Django 4.2.3 on 2024-04-03 07:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("general", "0003_defaultavatar"),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("TEXT", "Văn bản"),
                            ("AUDIO", "Âm thanh"),
                            ("VIDEO", "Video"),
                            ("IMAGE", "Hình ảnh"),
                        ],
                        max_length=5,
                        null=True,
                    ),
                ),
                ("text", models.TextField(blank=True, null=True)),
                ("is_seen", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("update_at", models.DateTimeField(auto_now=True)),
                ("file", models.ManyToManyField(to="general.fileupload")),
                (
                    "sender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
