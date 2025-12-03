# Guide des Tests - Application Meteo

Ce document explique comment executer et comprendre les tests unitaires de l'application meteo.

## Table des matieres

1. [Installation](#installation)
2. [Execution des tests](#execution-des-tests)
3. [Structure des tests](#structure-des-tests)
4. [Couverture de code](#couverture-de-code)
5. [CI/CD](#cicd)

## Installation

### Installer les dependances de test

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Dependances utilisees

- **pytest** : Framework de test principal
- **pytest-cov** : Pour mesurer la couverture de code
- **pytest-mock** : Pour faciliter le mocking
- **fakeredis** : Mock de Redis en memoire (pas besoin de Redis reel)
- **responses** : Mock des requetes HTTP vers l'API OpenWeatherMap
- **flake8** : Linting du code Python

## Execution des tests

### Executer tous les tests

```bash
cd backend
pytest
```

### Executer avec la couverture de code

```bash
pytest --cov=app --cov-report=term-missing
```

### Executer avec un rapport HTML

```bash
pytest --cov=app --cov-report=html
```

Le rapport sera genere dans `backend/htmlcov/index.html`

### Executer un fichier de test specifique

```bash
pytest tests/test_app.py
pytest tests/test_utils.py
pytest tests/test_cache.py
```

### Executer un test specifique

```bash
pytest tests/test_app.py::TestHealthEndpoint::test_health_check
```

### Mode verbose (plus de details)

```bash
pytest -v
```

## Structure des tests

```
backend/
├── tests/
│   ├── __init__.py           # Initialisation du package
│   ├── conftest.py           # Fixtures pytest (configuration partagee)
│   ├── test_app.py           # Tests des endpoints API
│   ├── test_cache.py         # Tests de la gestion du cache
│   └── test_utils.py         # Tests des fonctions utilitaires
├── pytest.ini                # Configuration pytest
├── .coveragerc               # Configuration du coverage
└── requirements-dev.txt      # Dependances de developpement
```

### Fichiers de tests

#### `test_utils.py`
Teste les fonctions utilitaires comme :
- `normalize_city_name()` : normalisation des noms de villes

#### `test_app.py`
Teste tous les endpoints de l'API :
- `GET /health` : verification de sante
- `GET /weather` : recuperation de meteo par ville ou coordonnees
- `GET /search/cities` : recherche de villes avec autocompletion
- `POST /cache/clear` : vidage du cache

#### `test_cache.py`
Teste la gestion du cache LRU :
- Limitation du nombre d'entrees
- Suppression des entrees les plus anciennes
- Format des cles
- Expiration du cache

### Fixtures (conftest.py)

Les fixtures sont des fonctions reutilisables qui configurent l'environnement de test :

- **app** : Instance de l'application Flask en mode test
- **client** : Client de test pour faire des requetes HTTP
- **mock_redis** : Instance de FakeRedis qui remplace Redis
- **mock_api_key** : Cle API mockee pour les tests

## Concepts de mocking

### Pourquoi mocker ?

Le mocking permet de :
1. **Tester sans dependances externes** : Pas besoin de Redis reel ou d'appeler l'API OpenWeatherMap
2. **Controler les reponses** : On decide exactement ce que renvoie l'API
3. **Tester les cas d'erreur** : Simuler des erreurs reseau, timeouts, etc.
4. **Rapidite** : Les tests s'executent en quelques secondes

### Exemples de mocking

#### Mock de Redis avec FakeRedis
```python
@pytest.fixture
def mock_redis(monkeypatch):
    fake_redis = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(app_module, 'redis_client', fake_redis)
    return fake_redis
```

#### Mock de l'API OpenWeatherMap avec responses
```python
@responses.activate
def test_get_weather(client):
    responses.add(
        responses.GET,
        'http://api.openweathermap.org/data/2.5/weather',
        json={'name': 'Paris', ...},
        status=200
    )
    response = client.get('/weather?city=Paris')
```

## Couverture de code

### Qu'est-ce que la couverture de code ?

La couverture de code mesure le pourcentage de code execute par les tests.

- **Ligne** : Pourcentage de lignes executees
- **Branch** : Pourcentage de branches (if/else) testees

### Objectif de couverture

Pour ce projet, on vise environ **70-80%** de couverture, ce qui est raisonnable pour un projet educatif.

### Interpreter le rapport de couverture

Exemple de sortie :
```
Name           Stmts   Miss  Cover   Missing
--------------------------------------------
app.py           150     30    80%   45-50, 120-125
--------------------------------------------
TOTAL            150     30    80%
```

- **Stmts** : Nombre total de lignes
- **Miss** : Lignes non couvertes
- **Cover** : Pourcentage de couverture
- **Missing** : Numeros des lignes non testees

## CI/CD

### Workflow GitHub Actions

Le fichier `.github/workflows/ci.yml` execute automatiquement :

1. **Tests unitaires** sur chaque push/PR
2. **Linting** avec flake8
3. **Build Docker** des images
4. **Tests d'integration** avec Docker Compose

### Jobs du CI/CD

#### Job 1 : Tests unitaires
- Installation de Python 3.11
- Installation des dependances
- Linting avec flake8 (non bloquant)
- Execution de pytest avec coverage
- Upload du rapport de coverage vers Codecov

#### Job 2 : Build Docker
- Build de l'image backend
- Build de l'image frontend
- Utilisation du cache pour accelerer

#### Job 3 : Tests d'integration
- Demarrage de tous les services avec Docker Compose
- Test du endpoint `/health`
- Verification des logs
- Arret propre des services

### Voir les resultats du CI/CD

1. Allez sur GitHub dans l'onglet "Actions"
2. Selectionnez votre workflow
3. Vous verrez :
   - Badge vert : Tests passes
   - Badge rouge : Tests echoues
   - Logs detailles pour chaque job

## Bonnes pratiques

### Ecrire de bons tests

1. **Un test = une chose** : Chaque test verifie un comportement precis
2. **Nommage clair** : `test_get_weather_by_city_success` est meilleur que `test1`
3. **AAA Pattern** :
   - **Arrange** : Preparer les donnees
   - **Act** : Executer l'action
   - **Assert** : Verifier le resultat

Exemple :
```python
def test_normalize_city_with_spaces():
    # Arrange
    city = "Le Puy en Velay"

    # Act
    result = normalize_city_name(city)

    # Assert
    assert result == "le-puy-en-velay"
```

### Maintenir les tests

- Executez les tests avant chaque commit
- Ajoutez des tests pour chaque nouveau feature
- Corrigez immediatement les tests qui echouent
- Gardez le coverage au-dessus de 70%

## Commandes utiles

```bash
# Installer les dependances
pip install -r requirements.txt requirements-dev.txt

# Executer tous les tests
pytest

# Tests avec coverage
pytest --cov=app

# Tests avec rapport HTML
pytest --cov=app --cov-report=html

# Tests en mode verbose
pytest -v

# Tests avec affichage des prints
pytest -s

# Executer un seul fichier
pytest tests/test_app.py

# Voir les fixtures disponibles
pytest --fixtures

# Linting
flake8 .
```

## Troubleshooting

### Les tests echouent avec "ModuleNotFoundError"
```bash
# Assurez-vous d'etre dans le bon dossier
cd backend
# Reinstallez les dependances
pip install -r requirements.txt requirements-dev.txt
```

### FakeRedis ne fonctionne pas
```bash
# Reinstallez fakeredis
pip install --upgrade fakeredis
```

### Erreur avec responses
```bash
# Verifiez que le decorateur @responses.activate est present
# Verifiez que l'URL mockee correspond exactement
```

## Ressources

- [Documentation pytest](https://docs.pytest.org/)
- [Documentation fakeredis](https://github.com/cunla/fakeredis-py)
- [Documentation responses](https://github.com/getsentry/responses)
- [Guide du mocking en Python](https://realpython.com/python-mock-library/)

## Auteur

Projet realise pour le BUT 3 Informatique - TP03 Virtualisation Avancee
