# Generated by Django 4.2.3 on 2024-07-24 15:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0033_fileuploadaudio"),
    ]

    operations = [
        migrations.CreateModel(
            name="AvatarFrame",
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
                ("title", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "frame",
                    models.FileField(
                        blank=True, null=True, upload_to="assets/avatar-frame/"
                    ),
                ),
                ("coin_price", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Khung avatar",
                "verbose_name_plural": "Khung avatar",
            },
        ),
    ]
