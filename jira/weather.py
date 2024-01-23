import json
from datetime import datetime, timedelta

import requests

# Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
API_KEY = "5c957b8e9f02fa82a41cbe5cfe077bbb"
CITY = "Berlin"
UNIT = "metric"  # Use 'imperial' for Fahrenheit

import requests


def get_weather(
    api_key, city, unit="metric"
):  # 'imperial' for Fahrenheit, 'metric' for Celsius
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "units": "metric", "appid": api_key}

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


def display_weather(weather_data):
    if weather_data:
        print(f"Weather in {weather_data['name']}, {weather_data['sys']['country']}:")
        print(f"Temperature: {weather_data['main']['temp']}°C")
        print(f"Description: {weather_data['weather'][0]['description']}")
        print(f"Humidity: {weather_data['main']['humidity']}%")
        print(f"Wind Speed: {weather_data['wind']['speed']} m/s")
    else:
        print("No weather data available.")


if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual OpenWeatherMap API key
    API_KEY = "5c957b8e9f02fa82a41cbe5cfe077bbb"
    CITY = "Berlin"  # Replace with the desired city name

    weather_data = get_weather(API_KEY, CITY)

    if weather_data:
        display_weather(weather_data)
