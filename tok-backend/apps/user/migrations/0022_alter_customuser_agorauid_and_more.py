# Generated by Django 4.2.3 on 2024-04-19 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0021_customuser_stringeeuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="agoraUID",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="stringeeUID",
            field=models.TextField(blank=True, null=True),
        ),
    ]
