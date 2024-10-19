from api.filters import MeasurementFilter
from .models import Measurement
from .serializers import MeasurementSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class MeasurementViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer
    filterset_class = MeasurementFilter
