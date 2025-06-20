#!/bin/bash

# Startup script for GCP instances
set -e

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install Python and pip
apt-get install -y python3 python3-pip python3-venv

# Install Git
apt-get install -y git

# Install Nginx
apt-get install -y nginx

# Install monitoring tools
apt-get install -y htop iotop nethogs

# Create application directory
mkdir -p /opt/startup-website
chown ubuntu:ubuntu /opt/startup-website

# Create systemd service for the application
cat > /etc/systemd/system/startup-website.service << EOF
[Unit]
Description=Startup Website Application
After=network.target docker.service
Requires=docker.service

[Service]
Type=forking
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/startup-website
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx as reverse proxy
cat > /etc/nginx/sites-available/startup-website << EOF
server {
    listen 80;
    server_name _;

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Bridge endpoints
    location /bridge/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Frontend application
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support for development
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/startup-website /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t
systemctl reload nginx
systemctl enable nginx

# Configure log rotation
cat > /etc/logrotate.d/startup-website << EOF
/opt/startup-website/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload startup-website
    endscript
}
EOF

# Create logs directory
mkdir -p /opt/startup-website/logs
chown ubuntu:ubuntu /opt/startup-website/logs

# Install monitoring agent (optional)
curl -sSO https://dl.google.com/cloudagents/add-google-cloud-ops-agent-repo.sh
bash add-google-cloud-ops-agent-repo.sh --also-install

# Configure firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Set up automatic security updates
apt-get install -y unattended-upgrades
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades

# Create deployment script
cat > /opt/startup-website/deploy.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting deployment..."

# Pull latest code
cd /opt/startup-website
git pull origin main

# Build and restart services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "Deployment completed successfully!"
EOF

chmod +x /opt/startup-website/deploy.sh
chown ubuntu:ubuntu /opt/startup-website/deploy.sh

# Signal that startup is complete
echo "Startup script completed successfully" > /var/log/startup-script.log

