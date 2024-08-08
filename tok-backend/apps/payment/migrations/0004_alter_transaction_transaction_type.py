# Generated by Django 4.2.3 on 2024-07-19 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0003_alter_transaction_transaction_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="transaction_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("deposit", "Mua thóc"),
                    ("withdraw", "Rút thóc"),
                    ("uid", "Mua id"),
                ],
                default="deposit",
                max_length=50,
                null=True,
                verbose_name="Loại giao dịch",
            ),
        ),
    ]
