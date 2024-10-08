# Generated by Django 4.2.3 on 2024-05-20 10:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notification", "0007_alter_notification_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="notifications",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Người nhận",
            ),
        ),
    ]
