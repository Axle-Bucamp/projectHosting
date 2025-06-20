# API Documentation

## Healthcheck API (Port 5000)

Service de monitoring pour vérifier l'état des prototypes et services.

### Endpoints

#### GET /api/health
Vérification de l'état de l'API healthcheck.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "service": "healthcheck-api"
}
```

#### GET /api/projects
Récupère la liste de tous les projets avec leur statut.

**Response:**
```json
[
  {
    "id": 1,
    "name": "E-commerce Platform",
    "url": "https://demo-ecommerce.example.com",
    "status": "online",
    "last_checked": "2024-01-01T12:00:00",
    "response_time": 0.245
  }
]
```

#### POST /api/projects/{id}/check
Lance une vérification de santé pour un projet spécifique.

**Response:**
```json
{
  "project_id": 1,
  "url": "https://demo-ecommerce.example.com",
  "status": "online",
  "response_time": 0.245,
  "status_code": 200,
  "error_message": null,
  "checked_at": "2024-01-01T12:00:00"
}
```

#### POST /api/projects/check-all
Lance une vérification de santé pour tous les projets.

#### GET /api/projects/{id}/history
Récupère l'historique des vérifications pour un projet.

#### GET /api/stats
Récupère les statistiques globales.

**Response:**
```json
{
  "total_projects": 6,
  "status_counts": {
    "online": 4,
    "offline": 1,
    "maintenance": 1
  },
  "average_response_time": 0.312,
  "uptime_percentage": 66.67
}
```

## Project Bridge API (Port 5001)

Service de reverse proxy pour router les requêtes vers les différents services.

### Endpoints

#### GET /api/bridge/health
Vérification de l'état du service bridge.

#### GET /api/bridge/services
Récupère la liste des services enregistrés.

**Response:**
```json
[
  {
    "id": 1,
    "name": "E-commerce API",
    "type": "api",
    "target_url": "https://api.ecommerce.example.com",
    "path_prefix": "/api/ecommerce",
    "enabled": true,
    "auth_required": false,
    "rate_limit": 1000,
    "created_at": "2024-01-01T12:00:00"
  }
]
```

#### POST /api/bridge/services
Ajoute un nouveau service.

**Request Body:**
```json
{
  "name": "New Service",
  "type": "api",
  "target_url": "https://api.example.com",
  "path_prefix": "/api/new",
  "enabled": true,
  "auth_required": false,
  "rate_limit": 100
}
```

#### PUT /api/bridge/services/{id}
Met à jour un service existant.

#### GET /api/bridge/stats
Récupère les statistiques du bridge.

**Response:**
```json
{
  "total_services": 6,
  "active_services": 5,
  "requests_24h": 1250,
  "average_response_time": 0.156,
  "requests_by_service": [
    {
      "service": "E-commerce API",
      "requests": 450
    }
  ]
}
```

### Proxy Functionality

Toutes les requêtes vers des chemins non-API sont automatiquement routées vers les services appropriés basés sur les préfixes de chemin configurés.

**Exemple:**
- Requête: `GET /api/ecommerce/products`
- Routée vers: `https://api.ecommerce.example.com/products`

## Intégration Frontend

Le frontend React peut utiliser ces APIs pour :

1. **Afficher le statut des projets** via `/api/projects`
2. **Déclencher des vérifications** via `/api/projects/check-all`
3. **Afficher des statistiques** via `/api/stats` et `/api/bridge/stats`
4. **Router les requêtes** automatiquement via le bridge

## Configuration

### Variables d'environnement

```bash
# Healthcheck API
HEALTHCHECK_PORT=5000
DATABASE_URL=sqlite:///src/database/app.db

# Project Bridge
BRIDGE_PORT=5001
BRIDGE_DATABASE_URL=sqlite:///src/database/app.db
```

### Base de données

Les deux services utilisent SQLite pour la persistance des données. Les bases de données sont automatiquement initialisées au démarrage avec des données d'exemple.

## Déploiement

```bash
# Healthcheck API
cd services/healthcheck-api
source venv/bin/activate
pip install -r requirements.txt
python src/main.py

# Project Bridge
cd services/project-bridge
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

