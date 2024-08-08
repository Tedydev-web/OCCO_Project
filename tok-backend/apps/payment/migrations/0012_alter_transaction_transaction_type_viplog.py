# Generated by Django 4.2.3 on 2024-08-05 10:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payment", "0011_banking_alter_transaction_transaction_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="transaction_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("deposit", "Mua thóc"),
                    ("uid", "Mua id"),
                    ("avatar", "Mua khung avatar"),
                    ("gift", "Mua quà"),
                    ("withdraw", "Rút thóc"),
                    ("coinToAds", "Quảng bá"),
                    ("vip", "Mua VIP"),
                ],
                default="deposit",
                max_length=50,
                null=True,
                verbose_name="Loại giao dịch",
            ),
        ),
        migrations.CreateModel(
            name="VIPLog",
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
                ("vip", models.JSONField(default=dict)),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="Ngày tạo"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Cập nhật"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Người mua",
                    ),
                ),
            ],
        ),
    ]
