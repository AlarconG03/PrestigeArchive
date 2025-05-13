from .weather import get_weather

def weather_info(request):
    # Obtiene la ciudad de la sesión o usar Medellin por defecto
    city = request.session.get('weather_city', 'Medellin')
    weather = get_weather(city)
    return {'weather': weather}