from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Measurement
from .serializers import MeasurementSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .permissions import IsOwner
from rest_framework.permissions import IsAuthenticated

class MeasurementList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request):
        measurements = Measurement.objects.all()
        serializer = MeasurementSerializer(measurements, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MeasurementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MeasurementDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, pk):
        try:
            return Measurement.objects.get(pk=pk)
        except Measurement.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        measurement = self.get_object(pk)
        serializer = MeasurementSerializer(measurement)
        return Response(serializer.data)

    def put(self, request, pk):
        measurement = self.get_object(pk)
        serializer = MeasurementSerializer(measurement, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        measurement = self.get_object(pk)
        measurement.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
