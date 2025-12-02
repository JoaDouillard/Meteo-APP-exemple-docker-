#!/bin/bash

# Script de configuration du projet météo

echo "====================================="
echo "Configuration de l'application météo"
echo "====================================="
echo ""

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ Docker est installé : $(docker --version)"

# Vérifier que Docker Compose est installé
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé."
    exit 1
fi

echo "✅ Docker Compose est installé : $(docker compose version)"
echo ""

# Vérifier si la clé API existe
if [ ! -f "secrets/weather_api_key.txt" ]; then
    echo "⚠️  Le fichier secrets/weather_api_key.txt n'existe pas."
    echo ""
    echo "Pour obtenir une clé API gratuite :"
    echo "1. Allez sur : https://home.openweathermap.org/users/sign_up"
    echo "2. Créez un compte (gratuit)"
    echo "3. Récupérez votre clé API dans la section 'API keys'"
    echo ""
    read -p "Entrez votre clé API OpenWeatherMap : " api_key

    if [ -z "$api_key" ]; then
        echo "❌ Aucune clé API fournie. Configuration annulée."
        exit 1
    fi

    echo "$api_key" > secrets/weather_api_key.txt
    echo "✅ Clé API configurée dans secrets/weather_api_key.txt"
else
    echo "✅ Clé API déjà configurée"
fi

echo ""
echo "====================================="
echo "Démarrage de l'application..."
echo "====================================="
echo ""

# Construire et démarrer les services
docker compose up --build

# Note : Ctrl+C pour arrêter
# Pour arrêter complètement : docker compose down
