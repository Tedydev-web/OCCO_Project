# Generated by Django 4.2.3 on 2024-07-22 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("conversation", "0037_room_block_2_user_roomuser_notification_mode"),
    ]

    operations = [
        migrations.RemoveField(model_name="room", name="block_2_user",),
    ]
