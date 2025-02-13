from rest_framework.routers import DefaultRouter
from .views import MeasurementViewSet, ForecastViewSet, StationViewSet

router = DefaultRouter()

router.register(r'stations', StationViewSet)
router.register(r'measurements', MeasurementViewSet)
router.register(r'forecast', ForecastViewSet, basename='forecast')

urlpatterns = router.urls
