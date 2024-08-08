# Generated by Django 4.2.3 on 2024-07-25 14:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("conversation", "0041_alter_room_newest_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pinnedmessage",
            name="message",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="conversation.message",
            ),
        ),
    ]
