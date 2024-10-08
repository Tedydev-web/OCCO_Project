# Generated by Django 4.2.3 on 2024-04-15 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0011_defaultavatar_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fileupload",
            name="file_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("IMAGE", "Ảnh"),
                    ("VIDEO", "Video"),
                    ("AUDIO", "Audio"),
                    ("FILE", "File"),
                ],
                max_length=500,
                null=True,
            ),
        ),
    ]
