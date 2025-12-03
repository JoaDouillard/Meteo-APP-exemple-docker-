import pytest
import sys
import os
from unittest.mock import MagicMock

# Ajouter le dossier parent au path pour importer app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import fakeredis
from app import app as flask_app


@pytest.fixture
def app():
    """Fixture qui cree une instance de l'application Flask pour les tests"""
    flask_app.config.update({
        'TESTING': True,
    })
    return flask_app


@pytest.fixture
def client(app):
    """Fixture qui cree un client de test pour l'application"""
    return app.test_client()


@pytest.fixture
def mock_redis(monkeypatch):
    """Fixture qui remplace Redis par FakeRedis pour les tests"""
    fake_redis = fakeredis.FakeRedis(decode_responses=True)

    # Remplacer la connexion Redis dans le module app
    import app as app_module
    monkeypatch.setattr(app_module, 'redis_client', fake_redis)

    return fake_redis


@pytest.fixture
def mock_api_key(monkeypatch):
    """Fixture qui mock la cle API"""
    monkeypatch.setenv('WEATHER_API_KEY', 'test_api_key_123456')

    # Mock de la fonction get_api_key
    import app as app_module
    monkeypatch.setattr(app_module, 'API_KEY', 'test_api_key_123456')

    return 'test_api_key_123456'
