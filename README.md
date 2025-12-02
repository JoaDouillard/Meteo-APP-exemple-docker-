# Application Météo - Projet Docker Compose

Application web de météo containerisée avec Docker, démontrant l'utilisation de Docker Compose, Dockerfile et la gestion des secrets.

## Architecture

L'application est composée de 3 services :

- **Backend** : API Flask qui appelle l'API OpenWeatherMap
- **Redis** : Cache pour optimiser les requêtes API
- **Frontend** : Interface web avec Nginx

## Prérequis

- Docker
- Docker Compose
- Une clé API OpenWeatherMap (gratuite)

## Configuration

### 1. Obtenir une clé API OpenWeatherMap

1. Créez un compte gratuit sur [OpenWeatherMap](https://openweathermap.org/api)
2. Allez dans la section "API keys"
3. Copiez votre clé API

### 2. Configurer le secret

Créez le fichier `secrets/weather_api_key.txt` et collez votre clé API :

```bash
echo "VOTRE_CLE_API" > secrets/weather_api_key.txt
```

**IMPORTANT** : Ne committez JAMAIS ce fichier dans Git. Il est déjà dans le `.gitignore`.

## Démarrage de l'application

### Lancer tous les services

```bash
docker compose up --build
```

L'option `--build` reconstruit les images si nécessaire.

### Lancer en arrière-plan

```bash
docker compose up -d --build
```

## Accès à l'application

- **Frontend** : http://localhost:8080
- **API Backend** : http://localhost:5000
- **Redis** : localhost:6379

## Utilisation

1. Ouvrez votre navigateur sur http://localhost:8080
2. Entrez le nom d'une ville
3. Cliquez sur "Rechercher"
4. Les données météo s'affichent avec :
   - Température
   - Description météo
   - Humidité
   - Vitesse du vent
5. Un badge "Données en cache" apparaît si les données proviennent du cache Redis

## Endpoints API

### GET /weather?city={ville}

Récupère la météo pour une ville.

**Exemple** :
```bash
curl "http://localhost:5000/weather?city=Paris"
```

**Réponse** :
```json
{
  "city": "Paris",
  "temperature": 15.5,
  "description": "nuageux",
  "humidity": 75,
  "wind_speed": 3.5,
  "from_cache": false
}
```

### POST /cache/clear

Vide le cache Redis.

**Exemple** :
```bash
curl -X POST "http://localhost:5000/cache/clear"
```

### GET /health

Vérifie l'état du backend.

**Exemple** :
```bash
curl "http://localhost:5000/health"
```

## Gestion du cache

- Les données météo sont mises en cache pendant **5 minutes**
- Cela réduit le nombre de requêtes vers l'API OpenWeatherMap
- Le bouton "Vider le cache" permet de forcer une actualisation

## Commandes utiles

### Voir les logs

```bash
# Tous les services
docker compose logs -f

# Un service spécifique
docker compose logs -f backend
docker compose logs -f redis
docker compose logs -f frontend
```

### Arrêter l'application

```bash
docker compose down
```

### Arrêter et supprimer les volumes

```bash
docker compose down -v
```

### Reconstruire une image spécifique

```bash
docker compose build backend
docker compose build frontend
```

### Voir l'état des containers

```bash
docker compose ps
```

### Accéder au shell d'un container

```bash
docker compose exec backend sh
docker compose exec redis redis-cli
```

## Détails techniques

### Réseau

Un réseau bridge personnalisé `weather-network` est créé automatiquement par Docker Compose. Les services communiquent entre eux par leurs noms :

- Le backend accède à Redis via `redis:6379`
- Le frontend accède au backend via `backend:5000`

### Volumes

Un volume `redis-data` persiste les données Redis entre les redémarrages.

### Secrets

La clé API est montée en tant que secret dans `/run/secrets/weather_api_key` du container backend, conformément aux bonnes pratiques de sécurité.

### Dockerfiles

#### Backend (backend/Dockerfile)
- Image de base : `python:3.11-slim`
- Installation des dépendances Python
- Exposition du port 5000

#### Frontend (frontend/Dockerfile)
- Image de base : `nginx:alpine`
- Configuration Nginx personnalisée
- Fichiers HTML statiques

## Structure du projet

```
meteo-app/
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
├── secrets/
│   ├── weather_api_key.txt (à créer)
│   └── weather_api_key.txt.example
├── compose.yaml
├── .gitignore
└── README.md
```

## Démonstration des concepts

Ce projet démontre :

1. **Création d'images Docker** :
   - Dockerfile pour le backend Flask
   - Dockerfile pour le frontend Nginx

2. **Application multi-services** :
   - 3 services orchestrés avec Docker Compose
   - Réseau privé personnalisé
   - Dépendances entre services (depends_on)

3. **Gestion des secrets** :
   - Clé API montée via Docker secrets
   - Fichier exclu du contrôle de version
   - Lecture sécurisée depuis `/run/secrets/`

## Dépannage

### Le backend ne démarre pas

Vérifiez que le fichier `secrets/weather_api_key.txt` existe et contient votre clé API.

### Erreur "Ville non trouvée"

Vérifiez que votre clé API est valide et active sur OpenWeatherMap.

### Le cache ne fonctionne pas

Vérifiez que Redis est bien démarré :
```bash
docker compose ps redis
docker compose logs redis
```

### Problème de ports déjà utilisés

Si les ports 5000, 6379 ou 8080 sont déjà utilisés, modifiez-les dans `compose.yaml`.

## Auteur

Projet réalisé pour le TP03 - Réseau et Docker Compose

## Licence

Projet éducatif - Libre d'utilisation
