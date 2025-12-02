from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import redis
import json
import os
import unicodedata
import re

app = Flask(__name__)
CORS(app)

# Connexion à Redis pour le cache
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

# Configuration du cache LRU
MAX_CACHE_ENTRIES = 100

# Lecture du secret (clé API)
def get_api_key():
    secret_path = '/run/secrets/weather_api_key'
    if os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            return f.read().strip()
    # Fallback pour le développement
    return os.getenv('WEATHER_API_KEY', '')

API_KEY = get_api_key()
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"

# Fonction de normalisation des noms de villes
def normalize_city_name(city):
    """
    Normalise un nom de ville pour la recherche
    Ex: "Le Puy en Velay" -> "le puy-en-velay"
    """
    # Convertir en minuscules
    city = city.lower()

    # Remplacer les espaces par des tirets
    city = re.sub(r'\s+', '-', city)

    # Retirer les accents
    city = unicodedata.normalize('NFD', city)
    city = ''.join(char for char in city if unicodedata.category(char) != 'Mn')

    return city

# Gestion du cache LRU
def manage_cache_size():
    """
    Limite le cache à MAX_CACHE_ENTRIES entrées
    Supprime les plus anciennes si dépassement
    """
    # Compter les clés weather:* et cities:*
    weather_keys = redis_client.keys('weather:*')
    cities_keys = redis_client.keys('cities:*')

    total_keys = len(weather_keys) + len(cities_keys)

    if total_keys > MAX_CACHE_ENTRIES:
        # Supprimer les clés les plus anciennes
        keys_to_delete = total_keys - MAX_CACHE_ENTRIES

        # Récupérer toutes les clés avec leur TTL
        all_keys = weather_keys + cities_keys
        keys_with_ttl = []

        for key in all_keys:
            ttl = redis_client.ttl(key)
            if ttl > 0:  # Ignorer les clés sans TTL
                keys_with_ttl.append((key, ttl))

        # Trier par TTL (les plus petits = plus anciennes)
        keys_with_ttl.sort(key=lambda x: x[1])

        # Supprimer les plus anciennes
        for i in range(min(keys_to_delete, len(keys_with_ttl))):
            redis_client.delete(keys_with_ttl[i][0])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/search/cities', methods=['GET'])
def search_cities():
    """
    Recherche de villes avec autocomplétion
    Ex: /search/cities?q=Nice
    Retourne une liste de villes correspondantes
    """
    query = request.args.get('q', '')

    if not query or len(query) < 2:
        return jsonify([]), 200

    # Normaliser la recherche
    normalized_query = normalize_city_name(query)

    # Vérifier le cache Redis
    cache_key = f"cities:{normalized_query}"
    cached_data = redis_client.get(cache_key)

    if cached_data:
        data = json.loads(cached_data)
        return jsonify(data), 200

    # Appel à l'API Geocoding de OpenWeatherMap
    try:
        params = {
            'q': query,
            'limit': 10,  # Maximum 10 résultats
            'appid': API_KEY
        }
        response = requests.get(GEOCODING_URL, params=params)
        response.raise_for_status()

        cities_data = response.json()

        # Formater les résultats
        results = []
        for city in cities_data:
            result = {
                'name': city['name'],
                'country': city['country'],
                'state': city.get('state', ''),
                'lat': city['lat'],
                'lon': city['lon'],
                'display_name': f"{city['name']}, {city.get('state', '')}, {city['country']}".replace(', ,', ',').strip(', ')
            }
            results.append(result)

        # Mettre en cache pour 1 heure (les villes ne changent pas souvent)
        redis_client.setex(cache_key, 3600, json.dumps(results))

        # Gérer la taille du cache
        manage_cache_size()

        return jsonify(results), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Récupère la météo pour une ville ou des coordonnées
    Paramètres:
    - city: Nom de la ville
    - lat: Latitude (optionnel, utilisé avec lon)
    - lon: Longitude (optionnel, utilisé avec lat)
    """
    city = request.args.get('city', '')
    lat = request.args.get('lat', '')
    lon = request.args.get('lon', '')

    # Déterminer la clé de cache
    if lat and lon:
        cache_key = f"weather:coords:{lat},{lon}"
        search_params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'fr'
        }
    elif city:
        # Normaliser le nom de la ville pour le cache
        normalized_city = normalize_city_name(city)
        cache_key = f"weather:{normalized_city}"
        search_params = {
            'q': city,
            'appid': API_KEY,
            'units': 'metric',
            'lang': 'fr'
        }
    else:
        return jsonify({"error": "Aucune ville ou coordonnées fournie"}), 400

    # Vérifier le cache Redis
    cached_data = redis_client.get(cache_key)

    if cached_data:
        data = json.loads(cached_data)
        data['from_cache'] = True
        return jsonify(data), 200

    # Appel à l'API OpenWeatherMap
    try:
        response = requests.get(BASE_URL, params=search_params)
        response.raise_for_status()

        weather_data = response.json()

        # Formater les données
        result = {
            'city': weather_data['name'],
            'country': weather_data['sys']['country'],
            'temperature': weather_data['main']['temp'],
            'description': weather_data['weather'][0]['description'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': weather_data['wind']['speed'],
            'lat': weather_data['coord']['lat'],
            'lon': weather_data['coord']['lon'],
            'from_cache': False
        }

        # Mettre en cache pour 5 minutes
        redis_client.setex(cache_key, 300, json.dumps(result))

        # Gérer la taille du cache
        manage_cache_size()

        return jsonify(result), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    redis_client.flushdb()
    return jsonify({"message": "Cache cleared"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
