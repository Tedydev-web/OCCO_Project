# Generated by Django 4.2.3 on 2024-05-03 03:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("discovery", "0009_rename_end_time_livestreaminghistory_end_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="livestreaminghistory", name="end_at",),
        migrations.RemoveField(model_name="livestreaminghistory", name="start_at",),
        migrations.AddField(
            model_name="livestreaminghistory",
            name="ended_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="livestreaminghistory",
            name="started_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
    ]
