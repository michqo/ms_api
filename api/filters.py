from django_filters import rest_framework as filters
from .models import Measurement

class MeasurementFilter(filters.FilterSet):
    class Meta:
        model = Measurement
        fields = {
            'created_at': ['lt', 'gt'],
            'temperature': ['lt', 'gt'],
            'humidity': ['lt', 'gt'],
            'pressure': ['lt', 'gt'],
            'rain': ['lt', 'gt'],
            'wind_speed': ['lt', 'gt'],
            'wind_direction': ['lt', 'gt'],
        }
