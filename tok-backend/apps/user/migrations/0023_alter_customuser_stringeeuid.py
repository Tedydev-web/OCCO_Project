# Generated by Django 4.2.3 on 2024-04-19 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0022_alter_customuser_agorauid_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="stringeeUID",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
