# Generated by Django 5.1.2 on 2025-01-28 18:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_meteobluedata_alter_measurement_timestamp'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MeteoblueData',
            new_name='ForecastData',
        ),
    ]
