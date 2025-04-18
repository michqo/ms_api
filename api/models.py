from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User
from django.utils.timezone import now

class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city_name = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Measurement(models.Model):
    station = models.ForeignKey(Station, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now)
    temperature = models.FloatField()
    humidity = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Measured {self.temperature} at {self.created_at}"

class ForecastData(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    city_name = models.TextField()
    modelrun_utc = models.DateTimeField()
    utc_timeoffset = models.FloatField()
    generation_time_ms = models.FloatField()
    time = ArrayField(models.TextField(), default=list)
    temperature_mean = ArrayField(models.FloatField(), default=list)
    temperature_instant = ArrayField(models.FloatField(), default=list)
    temperature_max = ArrayField(models.FloatField(), default=list)
    temperature_min = ArrayField(models.FloatField(), default=list)
    felttemperature_mean = ArrayField(models.FloatField(), default=list)
    relativehumidity_mean = ArrayField(models.IntegerField(), default=list)
    windspeed_mean = ArrayField(models.FloatField(), default=list)
    sealevelpressure_mean = ArrayField(models.IntegerField(), default=list)
    precipitation = ArrayField(models.FloatField(), default=list)
    precipitation_hours = ArrayField(models.FloatField(), default=list)
    predictability = ArrayField(models.FloatField(), default=list)
    pictocode = ArrayField(models.IntegerField(), default=list)
    winddirection = ArrayField(models.IntegerField(), default=list)
    uvindex = ArrayField(models.IntegerField(), default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Forecast data at {self.created_at}"

class MeasurementStat(models.Model):
    station = models.ForeignKey('Station', on_delete=models.CASCADE)
    temperature = models.FloatField(null=True, blank=True)
    humidity = models.FloatField(null=True, blank=True)
    date = models.DateTimeField()  # changed from DateField to DateTimeField
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = (("station", "date"),)

    def __str__(self):
        return f"Stats for {self.station} on {self.date}"
