# Generated by Django 4.2.3 on 2024-07-19 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0005_alter_transaction_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="transaction",
            name="information_detail",
            field=models.JSONField(default=dict, verbose_name="Thông tin thêm"),
        ),
    ]
