# Generated by Django 4.2.3 on 2024-08-05 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("general", "0036_supportandtraining"),
    ]

    operations = [
        migrations.CreateModel(
            name="Vip",
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
                    "coin_price",
                    models.PositiveIntegerField(default=0, verbose_name="Số thóc"),
                ),
                (
                    "total_month",
                    models.PositiveIntegerField(default=1, verbose_name="Số tháng"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Gói VIP", "verbose_name_plural": "Gói VIP",},
        ),
        migrations.AlterField(
            model_name="appinformation",
            name="title",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="appinformation",
            name="value",
            field=models.TextField(blank=True, null=True, verbose_name="Nội dung"),
        ),
        migrations.AlterField(
            model_name="avatarframe",
            name="coin_price",
            field=models.PositiveIntegerField(default=0, verbose_name="Số thóc"),
        ),
        migrations.AlterField(
            model_name="avatarframe",
            name="is_active",
            field=models.BooleanField(
                default=True, verbose_name="Trạng thái hoạt động"
            ),
        ),
        migrations.AlterField(
            model_name="fileupload",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Ngày đăng"),
        ),
        migrations.AlterField(
            model_name="fileupload",
            name="file_name",
            field=models.TextField(
                blank=True,
                default="",
                max_length=500,
                null=True,
                verbose_name="Tên file",
            ),
        ),
        migrations.AlterField(
            model_name="fileupload",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Người upload",
            ),
        ),
        migrations.AlterField(
            model_name="report",
            name="fk_id",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="id"
            ),
        ),
        migrations.AlterField(
            model_name="report",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("MESSAGE", "Tin nhắn"),
                    ("BLOG", "Bài đăng"),
                    ("LIVE", "Live"),
                ],
                max_length=7,
                null=True,
                verbose_name="Loại",
            ),
        ),
    ]
