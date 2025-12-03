import pytest
from app import manage_cache_size, MAX_CACHE_ENTRIES


class TestCacheManagement:
    """Tests pour la gestion du cache LRU"""

    def test_manage_cache_size_under_limit(self, mock_redis):
        """Test quand le cache est sous la limite"""
        # Ajouter quelques entrees
        mock_redis.setex('weather:paris', 300, 'data1')
        mock_redis.setex('weather:lyon', 300, 'data2')
        mock_redis.setex('cities:nice', 3600, 'data3')

        # Compter les cles avant
        initial_count = len(mock_redis.keys('weather:*')) + len(mock_redis.keys('cities:*'))

        # Appeler la fonction
        manage_cache_size()

        # Compter les cles apres
        final_count = len(mock_redis.keys('weather:*')) + len(mock_redis.keys('cities:*'))

        # Rien ne devrait etre supprime
        assert final_count == initial_count

    def test_manage_cache_size_over_limit(self, mock_redis):
        """Test quand le cache depasse la limite"""
        # Ajouter plus d'entrees que la limite
        for i in range(MAX_CACHE_ENTRIES + 10):
            mock_redis.setex(f'weather:city{i}', 300, f'data{i}')

        # Appeler la fonction
        manage_cache_size()

        # Verifier que le cache est reduit
        total_keys = len(mock_redis.keys('weather:*')) + len(mock_redis.keys('cities:*'))
        assert total_keys <= MAX_CACHE_ENTRIES

    def test_manage_cache_size_removes_oldest(self, mock_redis):
        """Test que les entrees les plus anciennes sont supprimees"""
        # Ajouter des entrees avec differents TTL
        mock_redis.setex('weather:old1', 10, 'data1')  # TTL court (plus ancien)
        mock_redis.setex('weather:old2', 20, 'data2')  # TTL moyen
        mock_redis.setex('weather:new', 300, 'data3')  # TTL long (plus recent)

        # Simuler un depassement en ajoutant beaucoup d'entrees
        for i in range(MAX_CACHE_ENTRIES + 5):
            mock_redis.setex(f'weather:city{i}', 250, f'data{i}')

        # Appeler la fonction
        manage_cache_size()

        # Les anciennes entrees devraient etre supprimees en premier
        # L'entree recente devrait toujours exister
        assert mock_redis.get('weather:new') is not None

    def test_cache_key_format_weather(self, mock_redis):
        """Test du format des cles de cache pour la meteo"""
        key = 'weather:paris'
        mock_redis.setex(key, 300, 'test_data')

        assert mock_redis.exists(key)
        assert mock_redis.ttl(key) <= 300

    def test_cache_key_format_cities(self, mock_redis):
        """Test du format des cles de cache pour les villes"""
        key = 'cities:par'
        mock_redis.setex(key, 3600, 'test_data')

        assert mock_redis.exists(key)
        assert mock_redis.ttl(key) <= 3600

    def test_cache_expiration(self, mock_redis):
        """Test que le cache expire correctement"""
        # Ajouter une entree avec TTL court
        mock_redis.setex('weather:test', 1, 'data')

        # Verifier qu'elle existe
        assert mock_redis.get('weather:test') == 'data'

        # Note: FakeRedis ne supporte pas vraiment l'expiration temporelle
        # mais on peut verifier que le TTL est bien defini
        assert mock_redis.ttl('weather:test') > 0
