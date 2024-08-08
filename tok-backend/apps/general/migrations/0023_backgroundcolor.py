# Generated by Django 4.2.3 on 2024-07-18 02:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0022_adminproxy"),
    ]

    operations = [
        migrations.CreateModel(
            name="BackGroundColor",
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
                ("color", models.CharField(default="#FF0000")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
