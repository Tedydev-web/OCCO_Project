# Generated by Django 4.2.3 on 2024-06-14 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0019_alter_report_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="appconfig",
            name="note",
            field=models.TextField(blank=True, default="", verbose_name="Chú thích"),
        ),
    ]
