import pytest
from app import normalize_city_name


class TestNormalizeCityName:
    """Tests pour la fonction de normalisation des noms de villes"""

    def test_normalize_simple_city(self):
        """Test avec un nom de ville simple"""
        result = normalize_city_name("Paris")
        assert result == "paris"

    def test_normalize_city_with_spaces(self):
        """Test avec des espaces"""
        result = normalize_city_name("Le Puy en Velay")
        assert result == "le-puy-en-velay"

    def test_normalize_city_with_accents(self):
        """Test avec des accents"""
        result = normalize_city_name("Nîmes")
        assert result == "nimes"

    def test_normalize_city_mixed(self):
        """Test avec accents et espaces"""
        result = normalize_city_name("Saint-Étienne")
        assert result == "saint-etienne"

    def test_normalize_city_multiple_spaces(self):
        """Test avec plusieurs espaces consecutifs"""
        result = normalize_city_name("Aix   en   Provence")
        assert result == "aix-en-provence"

    def test_normalize_empty_string(self):
        """Test avec une chaine vide"""
        result = normalize_city_name("")
        assert result == ""

    def test_normalize_special_characters(self):
        """Test avec des caracteres speciaux"""
        result = normalize_city_name("Château-Thierry")
        assert result == "chateau-thierry"
