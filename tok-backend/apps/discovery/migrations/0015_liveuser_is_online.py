# Generated by Django 4.2.3 on 2024-05-07 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discovery", "0014_alter_livestreaminghistory_view"),
    ]

    operations = [
        migrations.AddField(
            model_name="liveuser",
            name="is_online",
            field=models.BooleanField(default=False),
        ),
    ]
