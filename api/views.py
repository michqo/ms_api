from api.filters import MeasurementFilter
from .models import Measurement, ForecastData
from .serializers import MeasurementSerializer, ForecastDataSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
import requests
from django.core.cache import cache
from datetime import timedelta
from django.conf import settings

class MeasurementViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
