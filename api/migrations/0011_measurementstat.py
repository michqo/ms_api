# Generated by Django 5.1.2 on 2025-03-29 07:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_forecastdata_city_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeasurementStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('temperature', models.FloatField(blank=True, null=True)),
                ('humidity', models.FloatField(blank=True, null=True)),
                ('pressure', models.FloatField(blank=True, null=True)),
                ('rain', models.FloatField(blank=True, null=True)),
                ('wind_speed', models.FloatField(blank=True, null=True)),
                ('wind_direction', models.FloatField(blank=True, null=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.station')),
            ],
            options={
                'unique_together': {('station', 'date')},
            },
        ),
    ]
