# Generated by Django 4.2.3 on 2024-04-02 14:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="DefaultAvatar",
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
                    "image",
                    models.ImageField(
                        default="constants/default_avatar.png",
                        upload_to="assets/default/avatar",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
