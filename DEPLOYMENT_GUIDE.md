# Guide de Déploiement Complet

## 🎯 Vue d'ensemble

Ce guide vous accompagne dans le déploiement complet du site web startup, de l'environnement local jusqu'à la production sur Google Cloud Platform.

## 📋 Prérequis

### Outils Requis

```bash
# Docker et Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# Ansible
pip install ansible ansible-lint

# Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### Comptes et Accès

1. **Compte Google Cloud Platform**
   - Projet GCP créé
   - Facturation activée
   - APIs nécessaires activées

2. **Nom de domaine**
   - Domaine enregistré
   - Accès aux DNS

3. **Repository Git**
   - GitHub/GitLab repository
   - Secrets configurés pour CI/CD

## 🚀 Déploiement Étape par Étape

### Étape 1 : Préparation Locale

```bash
# 1. Cloner le projet
git clone <your-repository-url>
cd startup-website

# 2. Configuration des variables
cp iac/terraform/terraform.tfvars.example iac/terraform/terraform.tfvars
cp iac/ansible/group_vars/all/main.yml.example iac/ansible/group_vars/all/main.yml

# 3. Éditer les variables
nano iac/terraform/terraform.tfvars
```

**Contenu terraform.tfvars :**
```hcl
project_id = "your-gcp-project-id"
domain_name = "your-domain.com"
region = "europe-west1"
zone = "europe-west1-b"
environment = "production"
```

### Étape 2 : Test Local

```bash
# 1. Test du frontend
cd services/frontend
npm install
npm run dev
# Vérifier http://localhost:5174

# 2. Test avec Docker Compose
cd ../../docker
docker-compose up -d
# Vérifier http://localhost:3000

# 3. Vérification des services
curl http://localhost:5000/api/health
curl http://localhost:5001/api/bridge/health
```

### Étape 3 : Configuration GCP

```bash
# 1. Authentification
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Activation des APIs
gcloud services enable compute.googleapis.com
gcloud services enable dns.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable container.googleapis.com

# 3. Création du service account
gcloud iam service-accounts create terraform-sa \
    --display-name="Terraform Service Account"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:terraform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"

# 4. Génération de la clé
gcloud iam service-accounts keys create terraform-key.json \
    --iam-account=terraform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Étape 4 : Déploiement Infrastructure

```bash
cd iac/terraform

# 1. Initialisation
terraform init

# 2. Workspace de production
terraform workspace new production
terraform workspace select production

# 3. Planification
terraform plan -var-file="terraform.tfvars"

# 4. Application
terraform apply -var-file="terraform.tfvars"

# 5. Récupération des outputs
terraform output
```

**Outputs importants :**
- `load_balancer_ip` : IP du load balancer
- `dns_name_servers` : Serveurs DNS à configurer
- `database_connection_name` : Nom de connexion DB

### Étape 5 : Configuration DNS

```bash
# 1. Récupérer les name servers
terraform output dns_name_servers

# 2. Configurer chez votre registrar
# Pointer votre domaine vers les name servers GCP

# 3. Vérifier la propagation
dig NS your-domain.com
dig A your-domain.com
```

### Étape 6 : Configuration des Serveurs

```bash
cd ../ansible

# 1. Mise à jour de l'inventaire
# Récupérer les IPs des instances depuis terraform output
nano inventory.yml

# 2. Configuration des secrets
ansible-vault create group_vars/all/vault.yml
# Ajouter les mots de passe et secrets

# 3. Test de connectivité
ansible all -i inventory.yml -m ping

# 4. Déploiement
ansible-playbook -i inventory.yml deploy.yml --ask-vault-pass
```

### Étape 7 : Configuration CI/CD

```bash
# 1. Secrets GitHub
# Dans Settings > Secrets and variables > Actions
GCP_SA_KEY=<contenu de terraform-key.json>
GCP_PROJECT_ID=<your-project-id>
SLACK_WEBHOOK=<webhook-url> (optionnel)

# 2. Push vers main pour déclencher le déploiement
git add .
git commit -m "feat: initial deployment"
git push origin main
```

## 🔧 Configuration Post-Déploiement

### Vérification des Services

```bash
# 1. Site web principal
curl -I https://your-domain.com

# 2. APIs
curl https://your-domain.com/api/health
curl https://your-domain.com/api/projects

# 3. Certificat SSL
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### Configuration du Monitoring

```bash
# 1. Accès Grafana
# https://your-domain.com:3001
# admin / admin_change_in_production

# 2. Configuration des alertes
# Importer les dashboards depuis monitoring/grafana/dashboards/

# 3. Vérification Prometheus
# https://your-domain.com:9090
```

### Optimisations de Performance

```bash
# 1. Configuration CDN
gcloud compute backend-services update startup-backend-service \
    --enable-cdn \
    --cache-mode=CACHE_ALL_STATIC

# 2. Optimisation base de données
gcloud sql instances patch startup-db \
    --database-flags=shared_preload_libraries=pg_stat_statements

# 3. Monitoring des performances
# Configurer les alertes dans Grafana
```

## 🔒 Sécurité et Maintenance

### Sauvegardes

```bash
# 1. Sauvegarde automatique base de données
gcloud sql backups create \
    --instance=startup-db \
    --description="Manual backup $(date)"

# 2. Sauvegarde du code
git tag v1.0.0
git push origin v1.0.0

# 3. Export de la configuration Terraform
terraform show > infrastructure-state.txt
```

### Mises à jour

```bash
# 1. Mise à jour des dépendances
cd services/frontend && npm update
cd ../healthcheck-api && pip install -r requirements.txt --upgrade

# 2. Mise à jour de l'infrastructure
cd iac/terraform
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"

# 3. Redéploiement des services
cd ../ansible
ansible-playbook -i inventory.yml deploy.yml --ask-vault-pass
```

### Monitoring et Alertes

```bash
# 1. Configuration des alertes Slack/Email
# Dans Grafana > Alerting > Notification channels

# 2. Métriques importantes à surveiller
# - Uptime des services
# - Temps de réponse
# - Utilisation CPU/Mémoire
# - Erreurs 5xx

# 3. Logs centralisés
# Accès via GCP Console > Logging
```

## 🚨 Troubleshooting

### Problèmes Courants

**1. Certificat SSL en attente**
```bash
# Vérifier la configuration DNS
dig A your-domain.com
# Attendre jusqu'à 24h pour la validation
```

**2. Services inaccessibles**
```bash
# Vérifier les health checks
gcloud compute backend-services get-health startup-backend-service --global
# Vérifier les logs
gcloud logging read "resource.type=gce_instance"
```

**3. Base de données inaccessible**
```bash
# Vérifier la connexion VPC
gcloud compute networks peerings list
# Tester la connectivité
gcloud sql connect startup-db --user=app_user
```

### Commandes de Debug

```bash
# État des instances
gcloud compute instances list

# Logs des services
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_name=startup-app-*"

# Métriques de performance
gcloud monitoring metrics list --filter="metric.type:compute"

# État du load balancer
gcloud compute forwarding-rules list
gcloud compute backend-services list
```

## 📊 Monitoring de Production

### KPIs à Surveiller

1. **Disponibilité**
   - Uptime > 99.9%
   - Temps de réponse < 500ms
   - Taux d'erreur < 0.1%

2. **Performance**
   - CPU < 70%
   - Mémoire < 80%
   - Disque < 85%

3. **Business**
   - Nombre de visiteurs
   - Projets consultés
   - Conversions store

### Alertes Recommandées

```yaml
# Exemple d'alerte Grafana
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
  for: 5m
  annotations:
    summary: "Taux d'erreur élevé détecté"

- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
  for: 5m
  annotations:
    summary: "Temps de réponse élevé"
```

## 🎯 Optimisations Avancées

### Performance

```bash
# 1. Optimisation des images
# Utiliser WebP et compression
# Configurer le cache CDN

# 2. Optimisation base de données
# Index sur les requêtes fréquentes
# Connection pooling

# 3. Optimisation réseau
# HTTP/2 activé
# Compression Gzip/Brotli
```

### Coûts

```bash
# 1. Instances préemptibles pour dev
gcloud compute instances create dev-instance \
    --preemptible \
    --machine-type=e2-micro

# 2. Autoscaling agressif
# Réduire min_replicas en heures creuses

# 3. Monitoring des coûts
# Configurer des budgets et alertes
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="Startup Website Budget" \
    --budget-amount=200
```

---

**Ce guide vous accompagne dans un déploiement production-ready. Pour toute question, consultez la documentation détaillée de chaque composant.**

