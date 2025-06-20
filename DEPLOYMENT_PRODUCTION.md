# Guide de Déploiement et d'Utilisation - Architecture Complète

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose
- Node.js 18+
- Python 3.11+
- Terraform
- Ansible
- Compte GCP avec facturation activée
- Compte Tailscale

### Installation Locale

```bash
# Cloner le projet
git clone <repository-url>
cd startup-website

# Démarrer tous les services
./docker/manage.sh start

# Accéder au site
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Admin (via Tailscale): http://admin.tailnet.local
```

## 🏗️ Architecture Déployée

### Services Principaux

1. **Site Web Public** (https://jylmqyrs.manus.space)
   - Frontend React optimisé
   - Contenu dynamique via API
   - Formulaire de contact fonctionnel

2. **Backend API** (Port 8000)
   - Flask avec SQLAlchemy
   - PostgreSQL pour les données
   - Redis pour le cache
   - JWT pour l'authentification

3. **Interface d'Administration** (Tailscale uniquement)
   - React avec authentification
   - Gestion complète du contenu
   - Monitoring système temps réel

4. **Infrastructure Cloud** (GCP)
   - Load Balancer HTTPS
   - Auto-scaling
   - DNS géré
   - Monitoring intégré

## 🔧 Gestion du Contenu

### Ajouter un Nouveau Projet

Via l'interface d'administration :

1. Se connecter via Tailscale
2. Aller dans "Projets" > "Ajouter"
3. Remplir les informations :
   ```json
   {
     "name": "Mon Nouveau Projet",
     "description": "Description du projet",
     "status": "online|maintenance|offline",
     "url": "https://mon-projet.com",
     "image_url": "https://image.com/projet.jpg",
     "technologies": ["React", "Node.js", "Docker"],
     "category": "web-app"
   }
   ```

### Modifier le Store

1. Interface Admin > "Store" > "Gérer les produits"
2. Ajouter/modifier les produits :
   ```json
   {
     "name": "Consultation DevOps",
     "description": "Audit et optimisation infrastructure",
     "price": 150,
     "currency": "EUR",
     "category": "consultation",
     "features": ["Audit complet", "Recommandations", "Support 30j"],
     "external_url": "https://calendly.com/consultation"
   }
   ```

### Gérer les Contacts

Les messages du formulaire de contact sont automatiquement stockés et visibles dans l'interface admin :
- Notifications en temps réel
- Export CSV
- Réponses directes par email
- Archivage automatique

## 🐳 Docker et Orchestration

### Services Docker

```yaml
services:
  frontend:      # Site web React
  backend-api:   # API Flask
  postgres:      # Base de données
  redis:         # Cache et sessions
  nginx:         # Reverse proxy
  prometheus:    # Monitoring
  grafana:       # Visualisation
```

### Commandes Utiles

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f [service]

# Redémarrer un service
docker-compose restart [service]

# Mise à jour
docker-compose pull && docker-compose up -d

# Backup base de données
docker-compose exec postgres pg_dump -U startup startup_db > backup.sql
```

## ☁️ Déploiement Cloud (GCP)

### Configuration Terraform

```bash
cd iac/terraform

# Initialiser
terraform init

# Planifier
terraform plan -var="project_id=mon-projet-gcp"

# Déployer
terraform apply

# Obtenir les outputs
terraform output
```

### Variables Importantes

```hcl
project_id = "mon-projet-gcp"
region = "europe-west1"
domain_name = "monsite.com"
tailscale_auth_key = "tskey-auth-xxxxx"
admin_email = "admin@monsite.com"
```

## 🔒 Sécurité et Accès Admin

### Configuration Tailscale

1. Créer un compte Tailscale
2. Installer sur votre machine :
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```

3. Configurer l'accès admin :
   ```bash
   # Sur le serveur
   sudo tailscale up --authkey=tskey-auth-xxxxx
   
   # Configurer les ACLs Tailscale
   {
     "acls": [
       {
         "action": "accept",
         "src": ["group:admins"],
         "dst": ["tag:admin-server:*"]
       }
     ]
   }
   ```

### Accès à l'Interface Admin

1. Se connecter au VPN Tailscale
2. Accéder à `http://admin-server.tailnet.local`
3. S'authentifier avec les credentials admin
4. Gérer le contenu en toute sécurité

## 📊 Monitoring et Maintenance

### Métriques Surveillées

- **Performance** : Temps de réponse, throughput
- **Erreurs** : Taux d'erreur 4xx/5xx
- **Infrastructure** : CPU, RAM, disque, réseau
- **Business** : Contacts, vues pages, conversions

### Alertes Configurées

- Services indisponibles
- Erreurs critiques
- Utilisation ressources élevée
- Certificats SSL expirés

### Dashboards Grafana

Accès via `http://monitoring.tailnet.local:3000`
- Dashboard système général
- Métriques applicatives
- Logs centralisés
- Alertes en temps réel

## 🔄 CI/CD et Déploiements

### Pipeline GitHub Actions

```yaml
# .github/workflows/ci-cd.yml
on:
  push:
    branches: [main]

jobs:
  test:
    # Tests automatisés
  build:
    # Build des images Docker
  deploy:
    # Déploiement automatique
```

### Processus de Déploiement

1. **Push sur main** → Déclenchement automatique
2. **Tests** → Validation du code
3. **Build** → Création des images Docker
4. **Deploy** → Mise à jour production
5. **Monitoring** → Vérification santé

## 🛠️ Maintenance et Troubleshooting

### Logs Importants

```bash
# Logs application
docker-compose logs -f backend-api

# Logs Nginx
docker-compose logs -f nginx

# Logs base de données
docker-compose logs -f postgres

# Métriques système
docker stats
```

### Problèmes Courants

**Service indisponible** :
```bash
# Vérifier le statut
docker-compose ps

# Redémarrer le service
docker-compose restart [service]
```

**Base de données lente** :
```bash
# Vérifier les connexions
docker-compose exec postgres psql -U startup -c "SELECT * FROM pg_stat_activity;"

# Optimiser
docker-compose exec postgres psql -U startup -c "VACUUM ANALYZE;"
```

**Espace disque plein** :
```bash
# Nettoyer Docker
docker system prune -a

# Nettoyer logs
sudo journalctl --vacuum-time=7d
```

## 📈 Optimisations et Évolutions

### Performance

- **CDN** : Intégration CloudFlare/GCP CDN
- **Cache** : Redis avancé avec TTL optimisé
- **Images** : Compression et formats modernes (WebP)
- **Database** : Index optimisés, requêtes analysées

### Sécurité

- **WAF** : Web Application Firewall
- **DDoS** : Protection anti-DDoS
- **Backup** : Sauvegardes automatisées
- **Audit** : Logs de sécurité détaillés

### Fonctionnalités

- **Analytics** : Google Analytics/Matomo
- **SEO** : Optimisation référencement
- **PWA** : Progressive Web App
- **API** : Versioning et documentation

## 📞 Support et Contact

### Documentation Technique
- Architecture : `/docs/ARCHITECTURE.md`
- API : `/docs/API_DOCUMENTATION.md`
- Déploiement : `/docs/DEPLOYMENT_GUIDE.md`

### Contacts
- **Technique** : tech@startup.com
- **Admin** : admin@startup.com
- **Urgences** : +33 X XX XX XX XX

---

**Architecture validée et prête pour la production**
*Dernière mise à jour : 19 juin 2025*

