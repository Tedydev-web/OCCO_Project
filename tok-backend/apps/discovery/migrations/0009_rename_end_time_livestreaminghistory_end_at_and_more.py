# Generated by Django 4.2.3 on 2024-05-03 03:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("discovery", "0008_messagelive_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="livestreaminghistory", old_name="end_time", new_name="end_at",
        ),
        migrations.RenameField(
            model_name="livestreaminghistory",
            old_name="start_time",
            new_name="start_at",
        ),
    ]
