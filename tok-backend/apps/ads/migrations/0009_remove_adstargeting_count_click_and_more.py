# Generated by Django 4.2.3 on 2024-07-31 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ads", "0008_alter_advertisement_direct_url"),
    ]

    operations = [
        migrations.RemoveField(model_name="adstargeting", name="count_click",),
        migrations.RemoveField(model_name="adstargeting", name="count_view",),
        migrations.AddField(
            model_name="adstargeting",
            name="clicked_date",
            field=models.JSONField(default=dict),
        ),
    ]
