from django_filters import rest_framework as filters
from .models import Measurement, Station, MeasurementStat
import datetime
from django.utils import timezone
from .models import Measurement

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
    timestamp_date = filters.DateFilter(method="filter_timestamp_date", label="Measurements for Specific Day (YYYY-MM-DD)")

    def filter_timestamp_date(self, queryset, _name, value):
        start = datetime.datetime.combine(value, datetime.time.min, tzinfo=timezone.get_current_timezone())
        end = datetime.datetime.combine(value, datetime.time.max, tzinfo=timezone.get_current_timezone())
        return queryset.filter(timestamp__gte=start, timestamp__lte=end)

    class Meta:
        model = Measurement
        fields = {
            'station': ['exact'],
            'created_at': ['lt', 'gt'],
            'timestamp': ['lt', 'gt'],
            'temperature': ['lt', 'gt'],
            'humidity': ['lt', 'gt'],
        }

class MeasurementStatFilter(filters.FilterSet):
    class Meta:
        model = MeasurementStat
        fields = {
            'station': ['exact'],
            'date': ['exact', 'lt', 'gt'],
        }
