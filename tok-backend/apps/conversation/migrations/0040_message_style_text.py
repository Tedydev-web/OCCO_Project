# Generated by Django 4.2.3 on 2024-07-23 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conversation", "0039_roomuser_block_status_private"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="style_text",
            field=models.TextField(blank=True, null=True),
        ),
    ]
