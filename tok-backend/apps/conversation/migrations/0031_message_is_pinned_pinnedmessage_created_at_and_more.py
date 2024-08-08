# Generated by Django 4.2.3 on 2024-07-17 06:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("conversation", "0030_message_forwarded_from_message_reply_to_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="is_pinned",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="pinnedmessage",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pinnedmessage",
            name="pinner",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="pinnedmessage",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
