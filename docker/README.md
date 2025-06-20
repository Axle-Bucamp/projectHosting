# Docker & CI/CD Documentation

## Vue d'ensemble

Cette section couvre la containerisation avec Docker et l'automatisation CI/CD pour le déploiement du site web startup.

## Architecture Docker

### Services

1. **Frontend** (Port 3000)
   - Image: Nginx Alpine avec build React
   - Optimisé pour la production
   - Gestion du routing côté client

2. **Healthcheck API** (Port 5000)
   - Image: Python 3.11 slim
   - API Flask pour monitoring
   - Base de données SQLite

3. **Project Bridge** (Port 5001)
   - Image: Python 3.11 slim
   - Reverse proxy intelligent
   - Gestion des services

4. **Nginx** (Port 80/443)
   - Reverse proxy principal
   - Terminaison SSL
   - Rate limiting

5. **PostgreSQL** (Port 5432)
   - Base de données principale
   - Données persistantes
   - Sauvegardes automatiques

6. **Redis** (Port 6379)
   - Cache en mémoire
   - Sessions utilisateur
   - Rate limiting

7. **Prometheus** (Port 9090)
   - Monitoring des métriques
   - Alertes automatiques
   - Rétention des données

8. **Grafana** (Port 3001)
   - Visualisation des métriques
   - Dashboards personnalisés
   - Alertes visuelles

## Déploiement Local

### Prérequis

```bash
# Docker et Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Commandes de base

```bash
# Démarrage complet
cd docker
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêt des services
docker-compose down

# Rebuild des images
docker-compose build --no-cache

# Restart d'un service spécifique
docker-compose restart frontend
```

### Variables d'environnement

```bash
# Fichier .env
NODE_ENV=production
POSTGRES_PASSWORD=secure_password
REDIS_PASSWORD=redis_password
GRAFANA_PASSWORD=admin_password
```

## Pipeline CI/CD

### GitHub Actions

Le pipeline automatise :

1. **Tests**
   - Tests unitaires frontend (Jest)
   - Tests API backend (pytest)
   - Linting et formatage

2. **Sécurité**
   - Scan de vulnérabilités (Trivy)
   - Audit des dépendances
   - Vérification des secrets

3. **Build**
   - Construction des images Docker
   - Push vers GitHub Container Registry
   - Tagging automatique

4. **Validation Infrastructure**
   - Validation Terraform
   - Lint Ansible
   - Tests de configuration

5. **Déploiement**
   - Staging automatique (branche develop)
   - Production avec approbation (branche main)
   - Rollback automatique en cas d'échec

### Environnements

#### Staging
- Déploiement automatique sur push develop
- Tests d'intégration complets
- Données de test

#### Production
- Déploiement manuel avec approbation
- Monitoring renforcé
- Sauvegardes automatiques

### Secrets GitHub

```bash
# Secrets requis
GCP_SA_KEY              # Clé de service GCP
GCP_PROJECT_ID          # ID du projet GCP
SLACK_WEBHOOK           # Webhook pour notifications
DOCKER_REGISTRY_TOKEN   # Token pour registry Docker
```

## Monitoring

### Health Checks

Chaque service expose un endpoint de santé :

```bash
# Frontend
curl http://localhost:3000/health

# Healthcheck API
curl http://localhost:5000/api/health

# Project Bridge
curl http://localhost:5001/api/bridge/health
```

### Métriques Prometheus

```yaml
# Métriques collectées
- http_requests_total
- http_request_duration_seconds
- container_cpu_usage_seconds_total
- container_memory_usage_bytes
- nginx_connections_active
```

### Dashboards Grafana

1. **Application Overview**
   - Requêtes par seconde
   - Temps de réponse
   - Taux d'erreur

2. **Infrastructure**
   - CPU et mémoire
   - Réseau et disque
   - Statut des containers

3. **Business Metrics**
   - Projets actifs
   - Uptime des services
   - Utilisation des APIs

## Sécurité

### Images Docker

```dockerfile
# Bonnes pratiques appliquées
- Images de base officielles
- Utilisateurs non-root
- Multi-stage builds
- Scan de vulnérabilités
- Secrets via variables d'environnement
```

### Réseau

```yaml
# Configuration réseau
networks:
  startup-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Volumes

```yaml
# Données persistantes
volumes:
  postgres-data:     # Base de données
  redis-data:        # Cache
  prometheus-data:   # Métriques
  grafana-data:      # Dashboards
  nginx-logs:        # Logs web
```

## Optimisations

### Performance

1. **Cache multi-niveaux**
   - CDN pour assets statiques
   - Redis pour sessions
   - Nginx pour reverse proxy

2. **Compression**
   - Gzip pour texte
   - Optimisation images
   - Minification JS/CSS

3. **Base de données**
   - Index optimisés
   - Connection pooling
   - Requêtes optimisées

### Coûts

1. **Ressources**
   - Autoscaling horizontal
   - Instances préemptibles
   - Monitoring des coûts

2. **Storage**
   - Lifecycle policies
   - Compression des logs
   - Archivage automatique

## Troubleshooting

### Problèmes courants

1. **Container qui ne démarre pas**
   ```bash
   docker-compose logs service-name
   docker inspect container-id
   ```

2. **Problèmes de réseau**
   ```bash
   docker network ls
   docker network inspect startup-network
   ```

3. **Volumes corrompus**
   ```bash
   docker volume ls
   docker volume inspect volume-name
   ```

### Commandes de diagnostic

```bash
# État des services
docker-compose ps

# Utilisation des ressources
docker stats

# Logs en temps réel
docker-compose logs -f --tail=100

# Accès shell dans un container
docker-compose exec service-name /bin/bash

# Nettoyage
docker system prune -a
```

## Maintenance

### Mises à jour

```bash
# Mise à jour des images
docker-compose pull
docker-compose up -d

# Mise à jour avec rebuild
docker-compose build --pull
docker-compose up -d
```

### Sauvegardes

```bash
# Sauvegarde base de données
docker-compose exec postgres pg_dump -U app_user startup_db > backup.sql

# Sauvegarde volumes
docker run --rm -v startup_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

### Monitoring des logs

```bash
# Rotation automatique configurée
/etc/logrotate.d/docker-containers

# Centralisation avec ELK Stack (optionnel)
- Elasticsearch
- Logstash  
- Kibana
```

