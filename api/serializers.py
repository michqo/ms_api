from djoser.serializers import UserSerializer, UserCreateSerializer as BaseUserSerializer
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Measurement, ForecastData, Station

class UserCreateSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = ['id', 'email', 'username', 'password']

class CurrentUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'username', 'password']

class StationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), default=serializers.CurrentUserDefault())
    city_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Station
        fields = '__all__'

class MeasurementSerializer(serializers.ModelSerializer):
    station = serializers.PrimaryKeyRelatedField(queryset=Station.objects.all())

    def validate_station(self, value):
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("The station does not belong to the current user.")
        return value

    class Meta:
        model = Measurement
        fields = '__all__'

class ForecastDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastData
        fields = '__all__'
