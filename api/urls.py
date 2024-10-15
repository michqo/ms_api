from django.urls import path
from .views import MeasurementDetail, MeasurementList

urlpatterns = [
    path('measurements', MeasurementList.as_view(), name='measurement-list'),
    path('measurements/<int:pk>', MeasurementDetail.as_view(), name='measurement-detail'),
]
