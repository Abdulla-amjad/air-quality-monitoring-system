from django.urls import path
from .views import (
    AQIDataView, HistoricalDataView, ForecastView, 
    AlertsView, CitiesView
)

urlpatterns = [
    path('aqi/', AQIDataView.as_view(), name='aqi'),
    path('historical/', HistoricalDataView.as_view(), name='historical'),
    path('forecast/', ForecastView.as_view(), name='forecast'),
    path('alerts/', AlertsView.as_view(), name='alerts'),
    path('cities/', CitiesView.as_view(), name='cities'),
]