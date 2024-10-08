# Generated by Django 4.2.3 on 2024-07-24 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("general", "0034_avatarframe"),
        ("user", "0044_alter_idcard_options_alter_idcard_status_verify_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="avatar_frame",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="general.avatarframe",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="country",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Vietnam", "Việt Nam"),
                    ("Laos", "Lào"),
                    ("Cambodia", "Cambodia"),
                    ("All", "Admin tổng"),
                ],
                default="Vietnam",
                max_length=50,
                null=True,
                verbose_name="Quốc gia",
            ),
        ),
    ]
