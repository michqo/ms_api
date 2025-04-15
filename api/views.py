from django import views
from api.filters import MeasurementFilter, StationFilter, MeasurementStatFilter  # added MeasurementStatFilter
from api.permissions import IsOwner
from .models import Measurement, ForecastData, Station, MeasurementStat  # added MeasurementStat
from .serializers import MeasurementSerializer, ForecastDataSerializer, StationSerializer, MeasurementStatSerializer  # added MeasurementStatSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
import requests
from django.core.cache import cache
from django.conf import settings
from django.db.models import Avg
from datetime import datetime, time, timedelta  # added timedelta

def convert_to_dms(lat, lon):
        lat_deg = int(lat)
        lat_min = int((abs(lat) - abs(lat_deg)) * 60)
        lat_sec = (abs(lat) - abs(lat_deg) - lat_min / 60) * 3600
        lat_direction = "N" if lat >= 0 else "S"
        lon_deg = int(lon)
        lon_min = int((abs(lon) - abs(lon_deg)) * 60)
        lon_sec = (abs(lon) - abs(lon_deg) - lon_min / 60) * 3600
        lon_direction = "E" if lon >= 0 else "W"
        return f"{abs(lat_deg)}°{lat_min}'{lat_sec:.1f}\"{lat_direction} {abs(lon_deg)}°{lon_min}'{lon_sec:.1f}\"{lon_direction}"

def coords_to_city_name(lat, lon):
    query = convert_to_dms(lat, lon)
    response = requests.get(
            "https://www.meteoblue.com/en/server/search/query3",
            params={"apikey": settings.METEOBLUE_API_KEY, "query": query},
        )
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])
        if results:
            return results[0].get("name", "")
        else:
            return ""

class PermissionMixin(viewsets.GenericViewSet):
    unauthorized_actions = [
        'list',
        'retrieve',
        'latest_measurement',
        'stats'
    ]

    def get_permissions(self):
        if self.action in self.unauthorized_actions:
            return []
        return [permission() for permission in getattr(self, 'permission_classes', [])]

class StationViewSet(PermissionMixin, viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filterset_class = StationFilter

    def get_queryset(self):
        queryset = self.queryset
        if self.action == 'list' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def update_city_name(self, instance):
        instance.city_name = coords_to_city_name(instance.latitude, instance.longitude)
        instance.save()
        return instance

    def perform_create(self, serializer):
        self.update_city_name(serializer.save())

    def perform_update(self, serializer):
        self.update_city_name(serializer.save())

class ForecastPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 30

class MeasurementViewSet(PermissionMixin, viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    filterset_class = MeasurementFilter
    pagination_class = ForecastPagination

    @action(detail=False, methods=['delete'], url_path='bulk-delete')
    def bulk_delete(self, request):
        f = MeasurementFilter(request.query_params, queryset=Measurement.objects.all())
        if not f.is_valid():
            return Response(f.errors, status=400)
        f.qs.delete()
        f_stats = MeasurementStatFilter(request.query_params, queryset=MeasurementStat.objects.all())
        f_stats.qs.delete()
        return Response({"message": "Measurements and their stats for the station have been deleted"})

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request):
        serializer = MeasurementSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=False, methods=['get'], url_path='latest')
    def latest_measurement(self, request):
        station_id = request.query_params.get("station")
        if not station_id:
            return Response({"error": "station query parameter is required"}, status=400)
        try:
            station = Station.objects.get(pk=station_id)
        except Station.DoesNotExist:
            return Response({"error": "Station not found"}, status=404)

        latest_measurement = Measurement.objects.filter(station=station).order_by('-timestamp').first()
        if not latest_measurement:
            return Response({"error": "No measurements found for this station"}, status=404)

        serializer = MeasurementSerializer(latest_measurement)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        station_id = request.query_params.get("station")
        timestamp_gt = request.query_params.get("timestamp__gt")
        timestamp_lt = request.query_params.get("timestamp__lt")
        if not station_id or not timestamp_gt or not timestamp_lt:
            return Response({"error": "station, timestamp__gt and timestamp__lt query parameters are required"}, status=400)
        try:
            start_dt = datetime.strptime(timestamp_gt, "%Y-%m-%d")
            end_dt = datetime.strptime(timestamp_lt, "%Y-%m-%d")
        except ValueError:
            return Response({"error": "Dates must be formatted as YYYY-MM-DD"}, status=400)
        try:
            station = Station.objects.get(pk=station_id)
        except Station.DoesNotExist:
            return Response({"error": "Station not found"}, status=404)
        start_date = start_dt.date()
        end_date = end_dt.date()
        if start_date > end_date:
            return Response({"error": "timestamp__gt must be before or equal to timestamp__lt"}, status=400)
        if (end_date - start_date).days > 7:
            return Response({"error": "The date range cannot be more than 7 days apart"}, status=400)
        stats_list = []
        today = timezone.localdate()
        current_date = end_date
        while current_date >= start_date:
            start = datetime.combine(current_date, time.min)
            end = datetime.combine(current_date, time.max)
            measurements = Measurement.objects.filter(station=station, timestamp__gte=start, timestamp__lte=end)
            if (current_date == today and measurements.count() > 0) or measurements.count() > 1:
                stat, created = MeasurementStat.objects.get_or_create(
                    station=station, date=datetime.combine(current_date, time.min)
                )
                if current_date == today or created:
                    aggregates = measurements.aggregate(
                        temperature=Avg("temperature"),
                        humidity=Avg("humidity"),
                    )
                    stat.temperature = aggregates["temperature"]
                    stat.humidity = aggregates["humidity"]
                    stat.save()
                stats_list.append(stat)
            current_date -= timedelta(days=1)
        return Response(MeasurementStatSerializer(stats_list, many=True).data)

class ForecastViewSet(PermissionMixin, viewsets.GenericViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        station_id = request.query_params.get("station")
        if not station_id:
            return Response({"error": "station query parameter is required"}, status=400)
        try:
            station = Station.objects.get(pk=station_id)
        except Station.DoesNotExist:
            return Response({"error": "Station not found"}, status=404)

        cache_key = f'meteoblue_data_{station_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Check if there is valid data in the database for the station's coordinates
        one_day_ago = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        valid_data = ForecastData.objects.filter(
            created_at__gte=one_day_ago,
            latitude=station.latitude,
            longitude=station.longitude,
        ).first()
        if valid_data:
            serialized_data = ForecastDataSerializer(valid_data).data
            cache.set(cache_key, serialized_data, timeout=3600)
            return Response(serialized_data)

        # Fetch new data from the API using the station's latitude and longitude
        params = {
            'lat': station.latitude,
            'lon': station.longitude,
            'apikey': settings.METEOBLUE_API_KEY,
        }
        response = requests.get('https://my.meteoblue.com/packages/basic-day', params=params)
        if response.status_code == 200:
            data = response.json()
            lat = data['metadata']['latitude']
            lon = data['metadata']['longitude']
            if lat != station.latitude or lon != station.longitude:
                station.latitude = lat
                station.longitude = lon
                station.save()
            city_name = coords_to_city_name(lat, lon)
            meteoblue_data = ForecastData.objects.create(
                latitude=lat,
                longitude=lon,
                city_name=city_name,
                modelrun_utc=data['metadata']['modelrun_utc'],
                utc_timeoffset=data['metadata']['utc_timeoffset'],
                generation_time_ms=data['metadata']['generation_time_ms'],
                time=data['data_day']['time'],
                temperature_instant=data['data_day']['temperature_instant'],
                precipitation=data['data_day']['precipitation'],
                predictability=data['data_day']['predictability'],
                temperature_mean=data['data_day']['temperature_mean'],
                temperature_max=data['data_day']['temperature_max'],
                temperature_min=data['data_day']['temperature_min'],
                felttemperature_mean=data['data_day']['felttemperature_mean'],
                relativehumidity_mean=data['data_day']['relativehumidity_mean'],
                windspeed_mean=data['data_day']['windspeed_mean'],
                sealevelpressure_mean=data['data_day']['sealevelpressure_mean'],
                precipitation_hours=data['data_day']['precipitation_hours'],
                pictocode=data['data_day']['pictocode'],
                winddirection=data['data_day']['winddirection'],
                uvindex=data['data_day']['uvindex']
            )
            serialized_data = ForecastDataSerializer(meteoblue_data).data
            cache.set(cache_key, serialized_data, timeout=3600)
            return Response(serialized_data)
        else:
            return Response({'error': 'Failed to fetch data from Meteoblue'}, status=response.status_code)
