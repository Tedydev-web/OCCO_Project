# Generated by Django 4.2.3 on 2024-05-15 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0016_remove_feedback_title_remove_feedback_user_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="feedback",
            options={"verbose_name": "Phản hồi", "verbose_name_plural": "Phản hồi"},
        ),
        migrations.AlterField(
            model_name="feedback",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo"),
        ),
    ]
