from django_filters import rest_framework as filters
from .models import Measurement, Station, MeasurementStat

class StationFilter(filters.FilterSet):
    class Meta:
        model = Station
        fields = {
            'name': ['exact'],
            'latitude': ['lt', 'gt'],
            'longitude': ['lt', 'gt'],
            'city_name': ['exact'],
            'created_at': ['lt', 'gt'],
        }

    @property
    def qs(self):
        parent = super().qs
        user = getattr(self.request, 'user', None)
        return parent.filter(user=user)

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

class MeasurementStatFilter(filters.FilterSet):
    class Meta:
        model = MeasurementStat
        fields = {
            'station': ['exact'],
            'date': ['exact', 'lt', 'gt'],
        }
