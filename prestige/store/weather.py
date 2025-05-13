import requests
import os
from django.conf import settings

def get_weather(city="Medellin"):
    """
    Obtiene la información del clima para una ciudad específica.
    Por defecto, usa Buenos Aires si no se especifica una ciudad.
    """
    api_key = settings.WEATHER_API_KEY
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=es"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lanza una excepción si hay un error HTTP
        
        data = response.json()
        weather_info = {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'icon_url': f"http://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png"
        }
        return weather_info
    except Exception as e:
        print(f"Error al obtener el clima: {e}")
        return None