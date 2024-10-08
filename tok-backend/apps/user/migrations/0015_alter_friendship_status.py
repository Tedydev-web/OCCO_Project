# Generated by Django 4.2.11 on 2024-04-09 07:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0014_friendship'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendship',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Đã gửi lời mời kết bạn'), ('ACCEPTED', 'Đang là bạn bè'), ('REJECTED', 'Từ chối kết bạn'), ('DELETED', 'Đã xóa')], default='pending', max_length=10),
        ),
    ]
