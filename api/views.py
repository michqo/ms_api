from api.filters import MeasurementFilter, StationFilter
from api.permissions import IsOwner
from .models import Measurement, ForecastData, Station
from .serializers import MeasurementSerializer, ForecastDataSerializer, StationSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import requests
from django.core.cache import cache
from django.conf import settings
import math

class StationViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    filterset_class = StationFilter

    def convert_to_dms(self, lat, lon):
        lat_deg = int(lat)
        lat_min = int((abs(lat) - abs(lat_deg)) * 60)
        lat_sec = (abs(lat) - abs(lat_deg) - lat_min / 60) * 3600
        lat_direction = "N" if lat >= 0 else "S"
        lon_deg = int(lon)
        lon_min = int((abs(lon) - abs(lon_deg)) * 60)
        lon_sec = (abs(lon) - abs(lon_deg) - lon_min / 60) * 3600
        lon_direction = "E" if lon >= 0 else "W"
        return f"{abs(lat_deg)}°{lat_min}'{lat_sec:.1f}\"{lat_direction} {abs(lon_deg)}°{lon_min}'{lon_sec:.1f}\"{lon_direction}"

    def update_city_name(self, instance):
        query = self.convert_to_dms(instance.latitude, instance.longitude)
        response = requests.get(
            "https://www.meteoblue.com/en/server/search/query3",
            params={"apikey": settings.METEOBLUE_API_KEY, "query": query},
        )
        if response.status_code == 200:
            data = response.json()
            instance.city_name = data.get("city_name", "")
            results = data.get("results", [])
            if results:
                instance.city_name = results[0].get("name", "")
            else:
                instance.city_name = ""
            instance.save()
        return instance

    def perform_create(self, serializer):
        self.update_city_name(serializer.save())

    def perform_update(self, serializer):
        self.update_city_name(serializer.save())

class MeasurementViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    filterset_class = MeasurementFilter

class ForecastViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cache_key = 'meteoblue_data'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        # Check if there is valid data in the database
        one_day_ago = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        valid_data = ForecastData.objects.filter(created_at__gte=one_day_ago).first()

        if valid_data:
            serialized_data = ForecastDataSerializer(valid_data).data
            cache.set(cache_key, serialized_data, timeout=3600)
            return Response(serialized_data)

        # Fetch new data from the API
        params = {
            'lat': '48.14646',
            'lon': '17.100002',
            'apikey': settings.METEOBLUE_API_KEY,
        }
        response = requests.get('https://my.meteoblue.com/packages/basic-day', params=params)
        if response.status_code == 200:
            data = response.json()
            meteoblue_data = ForecastData.objects.create(
                latitude=data['metadata']['latitude'],
                longitude=data['metadata']['longitude'],
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
