# Generated by Django 4.2.3 on 2024-07-23 09:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0032_stickercategory_index"),
    ]

    operations = [
        migrations.CreateModel(
            name="FileUploadAudio",
            fields=[],
            options={
                "verbose_name": "Quản lý audio",
                "verbose_name_plural": "Quản lý audio",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("general.fileupload",),
        ),
    ]
