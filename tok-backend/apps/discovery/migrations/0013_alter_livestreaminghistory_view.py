# Generated by Django 4.2.3 on 2024-05-07 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discovery", "0012_livestreaminghistory_host"),
    ]

    operations = [
        migrations.AlterField(
            model_name="livestreaminghistory",
            name="view",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
