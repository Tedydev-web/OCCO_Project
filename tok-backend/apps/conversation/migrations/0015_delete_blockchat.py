# Generated by Django 4.2.3 on 2024-04-16 03:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("conversation", "0014_alter_message_type"),
    ]

    operations = [
        migrations.DeleteModel(name="BlockChat",),
    ]
