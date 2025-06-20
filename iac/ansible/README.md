# Ansible Configuration Documentation

## Vue d'ensemble

Cette configuration Ansible automatise le déploiement et la configuration des serveurs pour le site web startup. Elle gère l'installation des dépendances, la configuration des services, et le déploiement de l'application.

## Structure

```
iac/ansible/
├── inventory.yml          # Inventaire des serveurs
├── deploy.yml             # Playbook principal
├── templates/             # Templates de configuration
│   ├── nginx-site.conf.j2
│   ├── .env.j2
│   ├── startup-website.service.j2
│   └── logrotate.j2
├── group_vars/           # Variables par groupe
└── host_vars/           # Variables par hôte
```

## Playbooks

### deploy.yml - Playbook principal

Ce playbook effectue les tâches suivantes :

1. **Mise à jour système**
   - Update des packages
   - Installation des dépendances

2. **Installation Docker**
   - Docker Engine
   - Docker Compose
   - Configuration utilisateur

3. **Configuration Nginx**
   - Installation et configuration
   - Reverse proxy vers les services
   - SSL/TLS avec Let's Encrypt

4. **Déploiement application**
   - Clone du repository Git
   - Build des containers Docker
   - Configuration des services systemd

5. **Sécurité**
   - Configuration firewall UFW
   - Headers de sécurité Nginx
   - Permissions appropriées

6. **Monitoring et logs**
   - Rotation des logs
   - Configuration monitoring

## Inventaire

### Structure de l'inventaire

```yaml
all:
  children:
    webservers:
      hosts:
        web-01:
          ansible_host: "IP_ADDRESS"
        web-02:
          ansible_host: "IP_ADDRESS"
    databases:
      hosts:
        db-01:
          ansible_host: "IP_ADDRESS"
```

### Variables importantes

```yaml
# Application
app_name: startup-website
app_environment: production
domain_name: your-domain.com

# Database
db_name: startup_db
db_user: app_user
db_password: "{{ vault_db_password }}"

# SSL
ssl_email: admin@your-domain.com
```

## Templates

### nginx-site.conf.j2

Configuration Nginx avec :
- Reverse proxy vers les services
- Headers de sécurité
- Compression Gzip
- Health checks
- Gestion des erreurs

### .env.j2

Variables d'environnement pour l'application :
- Configuration base de données
- URLs des APIs
- Secrets de sécurité
- Configuration monitoring

### startup-website.service.j2

Service systemd pour :
- Gestion automatique des containers
- Restart automatique
- Logging centralisé
- Sécurité renforcée

## Déploiement

### Prérequis

1. **Ansible installé**
   ```bash
   pip install ansible
   ```

2. **Accès SSH configuré**
   ```bash
   ssh-copy-id ubuntu@server-ip
   ```

3. **Variables sensibles chiffrées**
   ```bash
   ansible-vault create group_vars/all/vault.yml
   ```

### Commandes de déploiement

```bash
# Test de connectivité
ansible all -i inventory.yml -m ping

# Déploiement complet
ansible-playbook -i inventory.yml deploy.yml --ask-vault-pass

# Déploiement avec tags spécifiques
ansible-playbook -i inventory.yml deploy.yml --tags "docker,nginx"

# Mode dry-run
ansible-playbook -i inventory.yml deploy.yml --check
```

### Variables d'environnement

```bash
# Fichier group_vars/all/main.yml
app_version: "v1.0.0"
environment: "production"
domain_name: "startup-demo.com"

# Fichier group_vars/all/vault.yml (chiffré)
vault_db_password: "secure_password"
vault_jwt_secret: "jwt_secret_key"
vault_session_secret: "session_secret_key"
```

## Sécurité

### Ansible Vault

```bash
# Créer un fichier chiffré
ansible-vault create secrets.yml

# Éditer un fichier chiffré
ansible-vault edit secrets.yml

# Chiffrer un fichier existant
ansible-vault encrypt file.yml

# Déchiffrer un fichier
ansible-vault decrypt file.yml
```

### Variables sensibles

Toujours chiffrer :
- Mots de passe base de données
- Clés API
- Secrets JWT/Session
- Certificats privés

### Permissions

```yaml
# Exemple de configuration sécurisée
- name: Create config file
  template:
    src: config.j2
    dest: /etc/app/config.yml
    owner: app
    group: app
    mode: '0600'
```

## Monitoring

### Health Checks

```yaml
- name: Check application health
  uri:
    url: "http://{{ ansible_host }}/api/health"
    method: GET
  register: health_check
  failed_when: health_check.status != 200
```

### Log Management

```yaml
# Configuration logrotate
- name: Setup log rotation
  template:
    src: logrotate.j2
    dest: /etc/logrotate.d/startup-website
```

## Maintenance

### Mise à jour de l'application

```bash
# Redéploiement avec nouvelle version
ansible-playbook -i inventory.yml deploy.yml -e "app_version=v1.1.0"

# Restart des services
ansible webservers -i inventory.yml -m systemd -a "name=startup-website state=restarted"

# Vérification des logs
ansible webservers -i inventory.yml -m shell -a "tail -f /opt/startup-website/logs/app.log"
```

### Sauvegarde

```yaml
- name: Backup application data
  archive:
    path: "{{ app_dir }}"
    dest: "/backup/startup-website-{{ ansible_date_time.date }}.tar.gz"
    exclude_path:
      - "{{ app_dir }}/node_modules"
      - "{{ app_dir }}/.git"
```

## Troubleshooting

### Problèmes courants

1. **Échec de connexion SSH**
   ```bash
   ansible all -i inventory.yml -m ping -vvv
   ```

2. **Erreurs de permissions**
   ```bash
   ansible-playbook -i inventory.yml deploy.yml --become --ask-become-pass
   ```

3. **Services qui ne démarrent pas**
   ```bash
   ansible webservers -i inventory.yml -m systemd -a "name=startup-website status=status"
   ```

### Commandes de diagnostic

```bash
# Vérifier la configuration
ansible-playbook -i inventory.yml deploy.yml --syntax-check

# Mode verbeux
ansible-playbook -i inventory.yml deploy.yml -vvv

# Exécution étape par étape
ansible-playbook -i inventory.yml deploy.yml --step
```

## Bonnes pratiques

### Organisation

1. **Séparer les environnements**
   ```
   inventories/
   ├── production/
   ├── staging/
   └── development/
   ```

2. **Utiliser des rôles**
   ```
   roles/
   ├── common/
   ├── nginx/
   ├── docker/
   └── application/
   ```

3. **Versionner les playbooks**
   - Tags Git pour les releases
   - Documentation des changements
   - Tests automatisés

### Performance

1. **Parallélisation**
   ```yaml
   strategy: free
   serial: 2
   ```

2. **Cache des facts**
   ```yaml
   gather_facts: no
   ```

3. **Optimisation des tâches**
   ```yaml
   changed_when: false
   check_mode: no
   ```

