import pytest
import json
import responses
from unittest.mock import patch


class TestHealthEndpoint:
    """Tests pour l'endpoint /health"""

    def test_health_check(self, client):
        """Test que l'endpoint health retourne ok"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'


class TestWeatherEndpoint:
    """Tests pour l'endpoint /weather"""

    @responses.activate
    def test_get_weather_by_city_success(self, client, mock_redis, mock_api_key):
        """Test de recuperation de meteo par ville avec succes"""
        # Mock de la reponse de l'API OpenWeatherMap
        mock_response = {
            'name': 'Paris',
            'sys': {'country': 'FR'},
            'main': {
                'temp': 15.5,
                'humidity': 75
            },
            'weather': [{'description': 'nuageux'}],
            'wind': {'speed': 3.5},
            'coord': {'lat': 48.8566, 'lon': 2.3522}
        }

        responses.add(
            responses.GET,
            'http://api.openweathermap.org/data/2.5/weather',
            json=mock_response,
            status=200
        )

        # Appel de l'endpoint
        response = client.get('/weather?city=Paris')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['city'] == 'Paris'
        assert data['temperature'] == 15.5
        assert data['from_cache'] is False

    def test_get_weather_without_city(self, client):
        """Test sans parametres (doit retourner une erreur)"""
        response = client.get('/weather')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    @responses.activate
    def test_get_weather_from_cache(self, client, mock_redis, mock_api_key):
        """Test que la meteo est recuperee du cache la 2eme fois"""
        mock_response = {
            'name': 'Lyon',
            'sys': {'country': 'FR'},
            'main': {'temp': 18.0, 'humidity': 65},
            'weather': [{'description': 'ensoleille'}],
            'wind': {'speed': 2.0},
            'coord': {'lat': 45.75, 'lon': 4.85}
        }

        responses.add(
            responses.GET,
            'http://api.openweathermap.org/data/2.5/weather',
            json=mock_response,
            status=200
        )

        # Premier appel (pas en cache)
        response1 = client.get('/weather?city=Lyon')
        data1 = json.loads(response1.data)
        assert data1['from_cache'] is False

        # Deuxieme appel (doit venir du cache)
        response2 = client.get('/weather?city=Lyon')
        data2 = json.loads(response2.data)
        assert data2['from_cache'] is True
        assert data2['city'] == 'Lyon'

    @responses.activate
    def test_get_weather_by_coordinates(self, client, mock_redis, mock_api_key):
        """Test de recuperation de meteo par coordonnees"""
        mock_response = {
            'name': 'Nice',
            'sys': {'country': 'FR'},
            'main': {'temp': 22.0, 'humidity': 60},
            'weather': [{'description': 'ensoleille'}],
            'wind': {'speed': 4.0},
            'coord': {'lat': 43.7, 'lon': 7.25}
        }

        responses.add(
            responses.GET,
            'http://api.openweathermap.org/data/2.5/weather',
            json=mock_response,
            status=200
        )

        response = client.get('/weather?lat=43.7&lon=7.25')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['city'] == 'Nice'
        assert data['lat'] == 43.7


class TestSearchCitiesEndpoint:
    """Tests pour l'endpoint /search/cities"""

    def test_search_cities_empty_query(self, client):
        """Test avec une requete vide"""
        response = client.get('/search/cities?q=')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    def test_search_cities_short_query(self, client):
        """Test avec une requete trop courte (< 2 caracteres)"""
        response = client.get('/search/cities?q=P')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    @responses.activate
    def test_search_cities_success(self, client, mock_redis, mock_api_key):
        """Test de recherche de villes avec succes"""
        mock_response = [
            {
                'name': 'Paris',
                'country': 'FR',
                'state': 'Ile-de-France',
                'lat': 48.8566,
                'lon': 2.3522
            },
            {
                'name': 'Paris',
                'country': 'US',
                'state': 'Texas',
                'lat': 33.6609,
                'lon': -95.5555
            }
        ]

        responses.add(
            responses.GET,
            'http://api.openweathermap.org/geo/1.0/direct',
            json=mock_response,
            status=200
        )

        response = client.get('/search/cities?q=Paris')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]['name'] == 'Paris'
        assert data[0]['country'] == 'FR'


class TestCacheClearEndpoint:
    """Tests pour l'endpoint /cache/clear"""

    def test_clear_cache(self, client, mock_redis):
        """Test de vidage du cache"""
        # Ajouter quelque chose dans le cache
        mock_redis.set('test_key', 'test_value')
        assert mock_redis.get('test_key') == 'test_value'

        # Vider le cache
        response = client.post('/cache/clear')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data

        # Verifier que le cache est vide
        assert mock_redis.get('test_key') is None
