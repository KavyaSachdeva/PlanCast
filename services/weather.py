import os
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from config.settings import settings


class WeatherService:
    def __init__(self):
        self.api_key = settings.WEATHERAPI_API_KEY
        self.base_url = "http://api.weatherapi.com/v1"

        if not self.api_key:
            raise Exception(
                "WEATHERAPI_API_KEY not found in environment variables")

    def get_current_weather(self, location: str = "New York") -> Dict:
        """Get current weather for a location"""
        try:
            url = f"{self.base_url}/current.json"
            params = {
                'key': self.api_key,
                'q': location,
                'aqi': 'no'  # No air quality data to keep it simple
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            current = data['current']
            location_data = data['location']

            return {
                'location': location_data['name'],
                'temperature': current['temp_c'],
                'feels_like': current['feelslike_c'],
                'humidity': current['humidity'],
                'description': current['condition']['text'],
                'icon': current['condition']['icon'],
                'wind_speed': current['wind_kph'],
                'wind_dir': current['wind_dir'],
                'precipitation': current.get('precip_mm', 0),
                'timestamp': datetime.now().isoformat()
            }

        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            return {}

    def get_weather_forecast(self, location: str = "New York", date: str = None) -> Dict:
        """Get weather forecast for a specific date and location"""
        try:
            # If no date specified, get current weather
            if not date:
                return self.get_current_weather(location)

            # Parse date
            if date.lower() in ['today', 'now']:
                target_date = datetime.now()
            elif date.lower() == 'tomorrow':
                target_date = datetime.now() + timedelta(days=1)
            else:
                # Try to parse date string
                try:
                    target_date = datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    # Try other common formats
                    target_date = datetime.strptime(date, '%m/%d/%Y')

            # Get 3-day forecast (free tier limit)
            url = f"{self.base_url}/forecast.json"
            params = {
                'key': self.api_key,
                'q': location,
                'days': 3,
                'aqi': 'no'
            }

            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            forecast_days = data['forecast']['forecastday']

            # Find forecast for target date
            target_date_str = target_date.strftime('%Y-%m-%d')
            daily_forecast = None

            for day in forecast_days:
                if day['date'] == target_date_str:
                    daily_forecast = day
                    break

            if daily_forecast:
                day_data = daily_forecast['day']
                return {
                    'location': data['location']['name'],
                    'date': target_date_str,
                    'temperature': day_data['avgtemp_c'],
                    'max_temp': day_data['maxtemp_c'],
                    'min_temp': day_data['mintemp_c'],
                    # WeatherAPI doesn't provide feels_like for forecasts
                    'feels_like': day_data['avgtemp_c'],
                    'humidity': day_data['avghumidity'],
                    'description': day_data['condition']['text'],
                    'icon': day_data['condition']['icon'],
                    'wind_speed': day_data['maxwind_kph'],
                    'precipitation': day_data['totalprecip_mm'],
                    'precipitation_chance': day_data['daily_chance_of_rain'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'location': data['location']['name'],
                    'date': target_date_str,
                    'error': 'No forecast available for this date'
                }

        except requests.exceptions.RequestException as e:
            print(f"Weather API error: {e}")
            return {}
        except Exception as e:
            print(f"Error parsing date: {e}")
            return {}

    def check_weather_for_event(self, event_date: str, location: str = "New York") -> Dict:
        """Check weather for a specific event date"""
        forecast = self.get_weather_forecast(location, event_date)

        if not forecast or 'error' in forecast:
            return {
                'event_date': event_date,
                'location': location,
                'weather_available': False,
                'message': 'Weather forecast not available'
            }

        # Return raw weather data for LLM to interpret
        return {
            'event_date': event_date,
            'location': location,
            'weather_available': True,
            'temperature': forecast.get('temperature', 0),
            'max_temp': forecast.get('max_temp', 0),
            'min_temp': forecast.get('min_temp', 0),
            'description': forecast.get('description', ''),
            'precipitation_chance': forecast.get('precipitation_chance', 0),
            'precipitation': forecast.get('precipitation', 0),
            'humidity': forecast.get('humidity', 0),
            'wind_speed': forecast.get('wind_speed', 0),
            'raw_data': forecast  # Include all raw data for LLM analysis
        }

    def get_weather_summary(self, location: str = "New York") -> str:
        """Get a simple weather summary for a location"""
        weather = self.get_current_weather(location)

        if not weather:
            return f"Weather information unavailable for {location}"

        temp = weather.get('temperature', 0)
        description = weather.get('description', '')

        return f"Current weather in {location}: {temp}°C, {description}"
