# Generated by Django 4.2.3 on 2024-05-08 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discovery", "0018_alter_livestreaminghistory_country_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="livestreaminghistory",
            name="country",
            field=models.CharField(
                blank=True,
                choices=[("VI", "Việt Nam"), ("--", "--")],
                max_length=255,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="livestreaminghistory",
            name="side",
            field=models.CharField(
                blank=True,
                choices=[
                    ("NORTH", "Miền bắc"),
                    ("CENTRAL", "Miền trung"),
                    ("SOUTH", "Miền nam"),
                    ("ALL", "Toàn quốc"),
                ],
                max_length=255,
                null=True,
            ),
        ),
    ]
