from django_filters import rest_framework as filters
from .models import Measurement

class MeasurementFilter(filters.FilterSet):
    class Meta:
        model = Measurement
        fields = {
            'station': ['exact'],
            'created_at': ['lt', 'gt'],
            'timestamp': ['lt', 'gt'],
            'temperature': ['lt', 'gt'],
            'humidity': ['lt', 'gt'],
            'pressure': ['lt', 'gt'],
            'rain': ['lt', 'gt'],
            'wind_speed': ['lt', 'gt'],
            'wind_direction': ['lt', 'gt'],
        }
