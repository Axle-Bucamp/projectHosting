# Startup Website - Architecture Moderne Cloud

🚀 **Site web professionnel avec infrastructure cloud complète**

Un projet de site web moderne utilisant les dernières technologies cloud, avec une architecture scalable et des pratiques DevOps avancées.

## 🎯 Aperçu du Projet

Ce projet démontre une architecture web moderne complète avec :
- **Frontend React** moderne et responsive
- **APIs Backend** robustes avec monitoring
- **Infrastructure cloud** GCP avec Terraform
- **Déploiement automatisé** avec Ansible
- **CI/CD** avec GitHub Actions
- **Containerisation** Docker complète
- **Monitoring** et observabilité

## 🏗️ Architecture

```
startup-website/
├── services/                 # Services applicatifs
│   ├── frontend/            # Application React
│   ├── healthcheck-api/     # API de monitoring
│   └── project-bridge/      # Reverse proxy intelligent
├── iac/                     # Infrastructure as Code
│   ├── terraform/           # Provisioning GCP
│   └── ansible/             # Configuration serveurs
├── docker/                  # Containerisation
│   ├── docker-compose.yml   # Orchestration locale
│   └── nginx/               # Configuration proxy
└── .github/workflows/       # CI/CD Pipeline
```

## 🚀 Démarrage Rapide

### Prérequis

```bash
# Docker et Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Python 3.11+
apt-get install -y python3 python3-pip
```

### Lancement Local

```bash
# 1. Cloner le projet
git clone <repository-url>
cd startup-website

# 2. Démarrer avec Docker Compose
cd docker
docker-compose up -d

# 3. Accéder aux services
# Frontend: http://localhost:3000
# API Health: http://localhost:5000
# Monitoring: http://localhost:9090
```

### Développement

```bash
# Frontend en mode développement
cd services/frontend
npm install
npm run dev

# API Backend
cd services/healthcheck-api
pip install -r requirements.txt
python src/main.py
```

## 🛠️ Technologies Utilisées

### Frontend
- **React 18** - Framework UI moderne
- **Vite** - Build tool rapide
- **Tailwind CSS** - Framework CSS utility-first
- **React Router** - Navigation côté client

### Backend
- **Flask** - Framework web Python
- **SQLite/PostgreSQL** - Base de données
- **Redis** - Cache et sessions
- **Nginx** - Reverse proxy et load balancer

### Infrastructure
- **Google Cloud Platform** - Cloud provider
- **Terraform** - Infrastructure as Code
- **Ansible** - Configuration management
- **Docker** - Containerisation
- **Kubernetes** - Orchestration (optionnel)

### DevOps
- **GitHub Actions** - CI/CD Pipeline
- **Prometheus** - Monitoring des métriques
- **Grafana** - Visualisation des données
- **Let's Encrypt** - Certificats SSL automatiques

## 📊 Fonctionnalités

### Site Web
- ✅ **Page d'accueil** avec hero section moderne
- ✅ **Section Prototypes** avec statuts en temps réel
- ✅ **Store** avec liens vers plateformes externes
- ✅ **Design responsive** mobile et desktop
- ✅ **Images optimisées** et intégrées

### APIs
- ✅ **Health Check API** pour monitoring
- ✅ **Project Bridge** pour reverse proxy
- ✅ **Gestion des projets** avec base de données
- ✅ **Métriques** et logging centralisé

### Infrastructure
- ✅ **Auto-scaling** avec load balancer
- ✅ **SSL/TLS** automatique
- ✅ **DNS** managé avec DNSSEC
- ✅ **Sauvegardes** automatiques
- ✅ **Monitoring** 24/7

## 🚀 Déploiement Production

### 1. Configuration GCP

```bash
# Authentification
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Activation des APIs
gcloud services enable compute.googleapis.com
gcloud services enable dns.googleapis.com
gcloud services enable sql-component.googleapis.com
```

### 2. Déploiement Infrastructure

```bash
cd iac/terraform

# Initialisation
terraform init

# Planification
terraform plan -var="project_id=YOUR_PROJECT" -var="domain_name=your-domain.com"

# Déploiement
terraform apply
```

### 3. Configuration Serveurs

```bash
cd iac/ansible

# Configuration des serveurs
ansible-playbook -i inventory.yml deploy.yml
```

### 4. CI/CD Automatique

Le pipeline GitHub Actions se déclenche automatiquement sur :
- **Push main** → Déploiement production
- **Push develop** → Déploiement staging
- **Pull Request** → Tests et validation

## 📈 Monitoring

### Métriques Disponibles
- **Performance** : Temps de réponse, throughput
- **Disponibilité** : Uptime, health checks
- **Infrastructure** : CPU, mémoire, réseau
- **Business** : Projets actifs, utilisateurs

### Dashboards
- **Grafana** : Visualisation temps réel
- **Prometheus** : Collecte des métriques
- **Logs** : Centralisation avec rotation

## 🔒 Sécurité

### Mesures Implémentées
- **HTTPS** obligatoire avec redirection
- **Headers de sécurité** (CSP, HSTS, etc.)
- **Rate limiting** sur les APIs
- **Firewall** configuré
- **Secrets** chiffrés avec Ansible Vault
- **Images Docker** scannées pour vulnérabilités

## 💰 Coûts Estimés

### GCP (Europe, par mois)
- **Compute Engine** : €50-150
- **Load Balancer** : €20
- **Cloud SQL** : €30-50
- **Storage** : €5-10
- **DNS** : €1
- **Total** : **€106-236/mois**

### Optimisations
- Instances préemptibles pour dev/staging
- Auto-scaling pour ajuster la capacité
- CDN pour réduire les coûts de bande passante

## 📚 Documentation

### Guides Détaillés
- [Infrastructure Terraform](iac/terraform/README.md)
- [Configuration Ansible](iac/ansible/README.md)
- [Docker & CI/CD](docker/README.md)
- [APIs Documentation](services/API_DOCUMENTATION.md)

### Résultats des Tests
- [Rapport de Tests](TEST_RESULTS.md)

## 🤝 Contribution

### Structure du Code
```bash
# Tests
npm test                    # Frontend
pytest tests/              # Backend

# Linting
npm run lint               # Frontend
flake8 src/               # Backend

# Build
npm run build             # Frontend
docker build .            # Containers
```

### Workflow Git
1. Fork le projet
2. Créer une branche feature
3. Commit avec messages conventionnels
4. Push et créer une Pull Request
5. Tests automatiques et review

## 📞 Support

### Problèmes Courants
- **Port déjà utilisé** : Changer les ports dans docker-compose.yml
- **Erreur SSL** : Vérifier la configuration DNS
- **API ne répond pas** : Vérifier les logs avec `docker-compose logs`

### Debugging
```bash
# Logs des services
docker-compose logs -f service-name

# État des containers
docker-compose ps

# Accès shell
docker-compose exec service-name /bin/bash
```

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🎉 Remerciements

- **React Team** pour le framework frontend
- **Google Cloud** pour l'infrastructure
- **Docker** pour la containerisation
- **Terraform** pour l'Infrastructure as Code
- **Communauté Open Source** pour les outils utilisés

---

**Développé avec ❤️ pour démontrer une architecture web moderne et scalable**

