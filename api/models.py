from django.db import models

class Measurement(models.Model):
    timestamp = models.DateTimeField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    pressure = models.FloatField()
    rain = models.FloatField()
    wind_speed = models.FloatField()
    wind_direction = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Measured {self.temperature} at {self.created_at}"

class ForecastData(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    modelrun_utc = models.DateTimeField()
    utc_timeoffset = models.FloatField()
    generation_time_ms = models.FloatField()
    time = models.JSONField()
    temperature_instant = models.JSONField()
    temperature_max = models.JSONField()
    temperature_min = models.JSONField()
    windspeed_mean = models.JSONField()
    sealevelpressure_mean = models.JSONField()
    precipitation = models.JSONField()
    precipitation_hours = models.JSONField()
    predictability = models.JSONField()
    pictocode = models.JSONField()
    winddirection = models.JSONField()
    uvindex = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Forecast data at {self.created_at}"
