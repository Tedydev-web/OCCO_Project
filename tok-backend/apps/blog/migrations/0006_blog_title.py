# Generated by Django 4.2.3 on 2024-06-20 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0005_alter_blog_options_blog_is_highlight_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="blog",
            name="title",
            field=models.CharField(default="", max_length=255),
        ),
    ]
