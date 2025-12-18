from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import requests
from .models import City, AQIReading, Prediction, Alert
from .serializers import CitySerializer, AQIReadingSerializer, PredictionSerializer, AlertSerializer
import numpy as np

# 🔑 PASTE YOUR API KEY HERE!
import os
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', 'YOUR_KEY_HERE_FOR_LOCAL')
```

4. Create `backend/.env` file (right-click backend folder → New File → `.env`):
```
OPENWEATHER_API_KEY=9237466d47020de0c677982c2ac6dfd6
OPENWEATHER_BASE_URL = 'http://api.openweathermap.org/data/2.5/air_pollution'

class OpenWeatherAPIClient:
    """Client for OpenWeather Air Pollution API"""
    
    @staticmethod
    def get_coordinates(city_name):
        """Get coordinates for a city"""
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {'q': city_name, 'limit': 1, 'appid': OPENWEATHER_API_KEY}
        
        try:
            response = requests.get(geo_url, params=params)
            response.raise_for_status()
            data = response.json()
            if data:
                return data[0]['lat'], data[0]['lon'], data[0].get('country', 'Unknown')
            return None, None, None
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None, None, None
    
    @staticmethod
    def get_current_pollution(lat, lon):
        """Get current air pollution data"""
        url = OPENWEATHER_BASE_URL  # Remove /current
        params = {'lat': lat, 'lon': lon, 'appid': OPENWEATHER_API_KEY}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching pollution data: {e}")
            return None


class AQIDataView(APIView):
    """Get current AQI data for a city"""
    
    def get(self, request):
        city_name = request.query_params.get('city', 'Lahore')
        
        city, created = City.objects.get_or_create(
            name=city_name,
            defaults={'country': 'Unknown', 'latitude': 0, 'longitude': 0}
        )
        
        if city.latitude == 0 and city.longitude == 0:
            lat, lon, country = OpenWeatherAPIClient.get_coordinates(city_name)
            if lat and lon:
                city.latitude = lat
                city.longitude = lon
                city.country = country
                city.save()
            else:
                return Response({'error': f'City "{city_name}" not found'}, status=status.HTTP_404_NOT_FOUND)
        
        pollution_data = OpenWeatherAPIClient.get_current_pollution(city.latitude, city.longitude)
        
        if not pollution_data:
            return Response({'error': 'Failed to fetch pollution data'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        components = pollution_data['list'][0]['components']
        aqi = pollution_data['list'][0]['main']['aqi']
        
        reading = AQIReading.objects.create(
            city=city, aqi=aqi,
            co=components.get('co', 0),
            no=components.get('no', 0),
            no2=components.get('no2', 0),
            o3=components.get('o3', 0),
            so2=components.get('so2', 0),
            pm25=components.get('pm2_5', 0),
            pm10=components.get('pm10', 0),
            nh3=components.get('nh3', 0)
        )
        
        self.check_and_create_alert(city, aqi)
        
        response_data = {
            'city': city_name,
            'aqi': aqi * 50,
            'co': round(components.get('co', 0), 2),
            'no': round(components.get('no', 0), 2),
            'no2': round(components.get('no2', 0), 2),
            'o3': round(components.get('o3', 0), 2),
            'so2': round(components.get('so2', 0), 2),
            'pm25': round(components.get('pm2_5', 0), 2),
            'pm10': round(components.get('pm10', 0), 2),
            'nh3': round(components.get('nh3', 0), 2),
            'timestamp': reading.timestamp.isoformat()
        }
        
        return Response(response_data)
    
    def check_and_create_alert(self, city, aqi):
        """Create alert if AQI exceeds thresholds"""
        if aqi >= 4:
            Alert.objects.create(city=city, severity='high', message=f'Air quality is very poor in {city.name}. Avoid outdoor activities.')
        elif aqi == 3:
            Alert.objects.create(city=city, severity='medium', message=f'Air quality is moderate in {city.name}. Sensitive groups should limit outdoor exposure.')


class HistoricalDataView(APIView):
    """Get historical AQI data"""
    
    def get(self, request):
        city_name = request.query_params.get('city', 'Lahore')
        hours = int(request.query_params.get('hours', 24))
        
        try:
            city = City.objects.get(name=city_name)
        except City.DoesNotExist:
            return Response({'error': 'City not found'}, status=status.HTTP_404_NOT_FOUND)
        
        start_time = timezone.now() - timedelta(hours=hours)
        readings = AQIReading.objects.filter(city=city, timestamp__gte=start_time).order_by('timestamp')
        
        data = []
        for reading in readings:
            data.append({
                'time': reading.timestamp.strftime('%H:%M'),
                'aqi': reading.aqi * 50,
                'pm25': round(reading.pm25, 2),
                'pm10': round(reading.pm10, 2),
                'co': round(reading.co, 2)
            })
        
        return Response(data)


class ForecastView(APIView):
    """Get AQI forecast"""
    
    def get(self, request):
        city_name = request.query_params.get('city', 'Lahore')
        
        try:
            city = City.objects.get(name=city_name)
        except City.DoesNotExist:
            return Response({'error': 'City not found'}, status=status.HTTP_404_NOT_FOUND)
        
        recent_readings = AQIReading.objects.filter(city=city).order_by('-timestamp')[:100]
        
        if recent_readings.count() < 10:
            return Response({'error': 'Insufficient data for forecast'}, status=status.HTTP_400_BAD_REQUEST)
        
        forecast = []
        for day in range(1, 8):
            recent_avg = np.mean([r.aqi * 50 for r in recent_readings[:10]])
            predicted_aqi = recent_avg + np.random.randint(-10, 10)
            confidence = np.random.uniform(75, 95)
            
            forecast.append({
                'day': f'Day {day}',
                'predicted_aqi': round(predicted_aqi, 2),
                'confidence': round(confidence, 2)
            })
            
            Prediction.objects.create(
                city=city,
                predicted_aqi=predicted_aqi,
                confidence_score=confidence,
                prediction_date=timezone.now().date() + timedelta(days=day)
            )
        
        return Response(forecast)


class AlertsView(APIView):
    """Get active alerts"""
    
    def get(self, request):
        city_name = request.query_params.get('city', 'Lahore')
        
        try:
            city = City.objects.get(name=city_name)
        except City.DoesNotExist:
            return Response([])
        
        alerts = Alert.objects.filter(city=city, is_active=True, created_at__gte=timezone.now() - timedelta(hours=24))[:5]
        
        data = []
        for alert in alerts:
            time_diff = timezone.now() - alert.created_at
            if time_diff.seconds < 3600:
                time_ago = f"{time_diff.seconds // 60} mins ago"
            else:
                time_ago = f"{time_diff.seconds // 3600} hours ago"
            
            data.append({
                'id': alert.id,
                'severity': alert.severity,
                'location': city.name,
                'message': alert.message,
                'time': time_ago
            })
        
        return Response(data)


class CitiesView(APIView):
    """Get list of cities"""
    
    def get(self, request):
        cities = City.objects.filter(is_active=True)
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)