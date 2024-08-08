# Generated by Django 4.2.3 on 2024-07-19 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0028_uidtrading_alter_aboutus_options_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="uidtrading",
            options={
                "verbose_name": "Danh sách UID",
                "verbose_name_plural": "Danh sách UID",
            },
        ),
        migrations.AlterField(
            model_name="uidtrading",
            name="uid",
            field=models.CharField(max_length=8, unique=True, verbose_name="UID"),
        ),
    ]
