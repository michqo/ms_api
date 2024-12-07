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
