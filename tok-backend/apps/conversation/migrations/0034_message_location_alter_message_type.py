# Generated by Django 4.2.3 on 2024-07-21 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conversation", "0033_room_background_color_room_background_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="location",
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="message",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("TEXT", "Văn bản"),
                    ("AUDIO", "Âm thanh"),
                    ("VIDEO", "Video"),
                    ("IMAGE", "Hình ảnh"),
                    ("FILE", "File"),
                    ("GIFT", "Quà tặng"),
                    ("CALL", "Gọi"),
                    ("VIDEO_CALL", "Gọi"),
                    ("HISTORY", "Lịch sử"),
                    ("LOCATION", "Vị trí"),
                ],
                max_length=10,
                null=True,
                verbose_name="Loại",
            ),
        ),
    ]
