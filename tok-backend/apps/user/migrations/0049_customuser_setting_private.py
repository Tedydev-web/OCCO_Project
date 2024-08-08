# Generated by Django 4.2.3 on 2024-07-30 16:49

import apps.user.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0048_usertimeline_direct_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="setting_private",
            field=models.JSONField(default=apps.user.models.init_setting),
        ),
    ]
