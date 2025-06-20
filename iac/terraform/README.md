# Terraform Infrastructure Documentation

## Vue d'ensemble

Cette configuration Terraform déploie une infrastructure complète sur Google Cloud Platform (GCP) pour héberger le site web startup avec une architecture moderne et scalable.

## Architecture

### Composants principaux

1. **Réseau (network.tf)**
   - VPC personnalisé avec subnet dédié
   - Règles de firewall pour HTTP/HTTPS/SSH
   - Configuration pour health checks

2. **Compute (compute.tf)**
   - Template d'instance avec Ubuntu 22.04
   - Groupe d'instances managé avec autoscaling
   - Health checks automatiques
   - IP statique pour le load balancer

3. **Load Balancer (load_balancer.tf)**
   - Load balancer global avec CDN
   - Certificat SSL managé automatiquement
   - Redirection HTTP vers HTTPS
   - Routage intelligent des requêtes

4. **DNS (dns.tf)**
   - Zone DNS managée avec DNSSEC
   - Enregistrements A pour le domaine principal
   - Configuration MX pour les emails
   - Sous-domaines API

5. **Storage (storage.tf)**
   - Bucket Cloud Storage pour les assets
   - Instance Cloud SQL PostgreSQL
   - Connexion VPC privée pour la base de données
   - Sauvegardes automatiques

## Déploiement

### Prérequis

1. **Compte GCP configuré**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **APIs activées**
   ```bash
   gcloud services enable compute.googleapis.com
   gcloud services enable dns.googleapis.com
   gcloud services enable sql-component.googleapis.com
   gcloud services enable storage.googleapis.com
   ```

3. **Clé SSH générée**
   ```bash
   ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
   ```

### Commandes de déploiement

```bash
# Initialisation
cd iac/terraform
terraform init

# Planification
terraform plan -var="project_id=your-project-id" -var="domain_name=your-domain.com"

# Application
terraform apply -var="project_id=your-project-id" -var="domain_name=your-domain.com"

# Destruction (si nécessaire)
terraform destroy
```

### Variables importantes

```hcl
# terraform.tfvars
project_id = "your-gcp-project-id"
domain_name = "your-domain.com"
region = "europe-west1"
machine_type = "e2-medium"
instance_count = 2
```

## Sécurité

### Mesures implémentées

1. **Réseau**
   - VPC isolé avec subnets privés
   - Règles de firewall restrictives
   - Accès SSH limité

2. **Base de données**
   - Connexion VPC privée
   - Chiffrement en transit et au repos
   - Sauvegardes automatiques

3. **SSL/TLS**
   - Certificats SSL managés automatiquement
   - Redirection forcée HTTPS
   - Headers de sécurité

4. **Monitoring**
   - Logs centralisés
   - Métriques de performance
   - Alertes automatiques

## Monitoring et Maintenance

### Health Checks

- **Application**: `/api/health`
- **Load Balancer**: Vérification automatique
- **Base de données**: Monitoring intégré

### Logs

- **Application**: `/opt/startup-website/logs/`
- **Nginx**: `/var/log/nginx/`
- **Système**: Journald

### Sauvegardes

- **Base de données**: Quotidiennes avec rétention 7 jours
- **Code**: Git repository
- **Assets**: Versioning Cloud Storage

## Scaling

### Autoscaling configuré

- **Min instances**: 2
- **Max instances**: 5
- **CPU target**: 70%
- **Load balancing target**: 80%

### Optimisations

- **CDN**: Cache global pour les assets statiques
- **Compression**: Gzip activé
- **Database**: Connection pooling

## Coûts

### Estimation mensuelle (région Europe)

- **Compute**: ~€50-150 (selon utilisation)
- **Load Balancer**: ~€20
- **Cloud SQL**: ~€30-50
- **Storage**: ~€5-10
- **DNS**: ~€1
- **Total**: ~€106-236/mois

### Optimisations de coûts

1. **Instances préemptibles** pour dev/staging
2. **Autoscaling** pour ajuster la capacité
3. **CDN** pour réduire la bande passante
4. **Monitoring** pour identifier les gaspillages

## Troubleshooting

### Problèmes courants

1. **SSL Certificate en attente**
   - Vérifier la configuration DNS
   - Attendre la propagation (jusqu'à 24h)

2. **Instances unhealthy**
   - Vérifier les logs de startup script
   - Contrôler les health checks

3. **Base de données inaccessible**
   - Vérifier la connexion VPC
   - Contrôler les règles de firewall

### Commandes utiles

```bash
# Vérifier l'état des ressources
terraform show

# Voir les outputs
terraform output

# Rafraîchir l'état
terraform refresh

# Importer une ressource existante
terraform import google_compute_instance.example projects/PROJECT_ID/zones/ZONE/instances/INSTANCE_NAME
```

