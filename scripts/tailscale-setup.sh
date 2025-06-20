#!/bin/bash

# Tailscale Setup and Management Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TAILSCALE_VERSION="1.56.1"
TAILNET_NAME="startup-admin"
ADMIN_HOSTNAME="startup-admin-$(hostname -s)"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Install Tailscale
install_tailscale() {
    log_info "Installing Tailscale..."
    
    # Add Tailscale's package signing key and repository
    curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.noarmor.gpg | tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
    curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/focal.list | tee /etc/apt/sources.list.d/tailscale.list
    
    # Update package list and install
    apt-get update
    apt-get install -y tailscale
    
    log_success "Tailscale installed successfully"
}

# Configure Tailscale
configure_tailscale() {
    local auth_key=$1
    
    if [ -z "$auth_key" ]; then
        log_error "Auth key is required"
        exit 1
    fi
    
    log_info "Configuring Tailscale with auth key..."
    
    # Start tailscaled if not running
    systemctl enable tailscaled
    systemctl start tailscaled
    
    # Authenticate with Tailscale
    tailscale up --authkey="$auth_key" --hostname="$ADMIN_HOSTNAME" --accept-routes --accept-dns
    
    log_success "Tailscale configured successfully"
}

# Setup firewall rules for Tailscale
setup_firewall() {
    log_info "Setting up firewall rules..."
    
    # Install ufw if not present
    apt-get install -y ufw
    
    # Allow Tailscale
    ufw allow in on tailscale0
    ufw allow out on tailscale0
    
    # Allow Tailscale UDP port
    ufw allow 41641/udp
    
    # Allow admin services only from Tailscale network
    ufw allow from 100.64.0.0/10 to any port 8080 comment "Admin interface"
    ufw allow from 100.64.0.0/10 to any port 9090 comment "Prometheus"
    ufw allow from 100.64.0.0/10 to any port 3001 comment "Grafana"
    
    # Enable firewall
    ufw --force enable
    
    log_success "Firewall configured for Tailscale"
}

# Create Tailscale service configuration
create_service_config() {
    log_info "Creating Tailscale service configuration..."
    
    cat > /etc/systemd/system/tailscale-admin.service << EOF
[Unit]
Description=Tailscale Admin Service
After=network.target tailscaled.service
Requires=tailscaled.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/tailscale up --accept-routes --accept-dns --hostname=$ADMIN_HOSTNAME
ExecStop=/usr/bin/tailscale down
User=root

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable tailscale-admin.service
    
    log_success "Tailscale service configuration created"
}

# Setup admin services
setup_admin_services() {
    log_info "Setting up admin services..."
    
    # Create admin user
    useradd -m -s /bin/bash admin || true
    usermod -aG sudo admin
    
    # Create admin directories
    mkdir -p /opt/admin/{config,logs,data}
    chown -R admin:admin /opt/admin
    
    # Create nginx configuration for admin services
    cat > /etc/nginx/sites-available/admin << EOF
server {
    listen 8080;
    server_name admin.startup.local;
    
    # Restrict access to Tailscale network
    allow 100.64.0.0/10;
    deny all;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 9090;
    server_name monitoring.startup.local;
    
    # Restrict access to Tailscale network
    allow 100.64.0.0/10;
    deny all;
    
    location / {
        proxy_pass http://localhost:9091;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}

server {
    listen 3001;
    server_name grafana.startup.local;
    
    # Restrict access to Tailscale network
    allow 100.64.0.0/10;
    deny all;
    
    location / {
        proxy_pass http://localhost:3002;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

    # Enable the site
    ln -sf /etc/nginx/sites-available/admin /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    
    log_success "Admin services configured"
}

# Generate Tailscale auth key (requires API key)
generate_auth_key() {
    local api_key=$1
    local tailnet=$2
    
    if [ -z "$api_key" ] || [ -z "$tailnet" ]; then
        log_error "API key and tailnet are required"
        exit 1
    fi
    
    log_info "Generating Tailscale auth key..."
    
    local auth_key=$(curl -s -X POST \
        -H "Authorization: Bearer $api_key" \
        -H "Content-Type: application/json" \
        -d '{
            "capabilities": {
                "devices": {
                    "create": {
                        "reusable": true,
                        "ephemeral": false,
                        "preauthorized": true,
                        "tags": ["tag:admin", "tag:startup"]
                    }
                }
            },
            "expirySeconds": 7776000
        }' \
        "https://api.tailscale.com/api/v2/tailnet/$tailnet/keys" | \
        jq -r '.key')
    
    if [ "$auth_key" != "null" ] && [ -n "$auth_key" ]; then
        echo "$auth_key"
        log_success "Auth key generated successfully"
    else
        log_error "Failed to generate auth key"
        exit 1
    fi
}

# Check Tailscale status
check_status() {
    log_info "Checking Tailscale status..."
    
    if systemctl is-active --quiet tailscaled; then
        log_success "Tailscaled is running"
        
        if tailscale status >/dev/null 2>&1; then
            log_success "Tailscale is connected"
            tailscale status
            
            # Show IP address
            local tailscale_ip=$(tailscale ip -4)
            log_info "Tailscale IP: $tailscale_ip"
            
            # Show admin URLs
            log_info "Admin URLs:"
            echo "  Admin Interface: http://$tailscale_ip:8080"
            echo "  Prometheus: http://$tailscale_ip:9090"
            echo "  Grafana: http://$tailscale_ip:3001"
        else
            log_warning "Tailscale is not connected"
        fi
    else
        log_error "Tailscaled is not running"
    fi
}

# Disconnect from Tailscale
disconnect() {
    log_info "Disconnecting from Tailscale..."
    
    tailscale down
    systemctl stop tailscaled
    systemctl disable tailscaled
    
    log_success "Disconnected from Tailscale"
}

# Remove Tailscale
remove_tailscale() {
    log_info "Removing Tailscale..."
    
    # Stop and disable services
    systemctl stop tailscaled || true
    systemctl disable tailscaled || true
    systemctl stop tailscale-admin || true
    systemctl disable tailscale-admin || true
    
    # Remove packages
    apt-get remove -y tailscale
    
    # Remove configuration files
    rm -rf /var/lib/tailscale
    rm -f /etc/systemd/system/tailscale-admin.service
    
    # Remove firewall rules
    ufw delete allow in on tailscale0 || true
    ufw delete allow out on tailscale0 || true
    ufw delete allow 41641/udp || true
    
    systemctl daemon-reload
    
    log_success "Tailscale removed"
}

# Setup monitoring for Tailscale
setup_monitoring() {
    log_info "Setting up Tailscale monitoring..."
    
    # Create monitoring script
    cat > /opt/admin/tailscale-monitor.sh << 'EOF'
#!/bin/bash

# Tailscale monitoring script
LOGFILE="/opt/admin/logs/tailscale-monitor.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Check if Tailscale is running
if ! systemctl is-active --quiet tailscaled; then
    echo "[$TIMESTAMP] ERROR: Tailscaled is not running" >> $LOGFILE
    systemctl start tailscaled
    exit 1
fi

# Check if connected to Tailscale network
if ! tailscale status >/dev/null 2>&1; then
    echo "[$TIMESTAMP] WARNING: Not connected to Tailscale network" >> $LOGFILE
    tailscale up --accept-routes --accept-dns
fi

# Log status
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "unknown")
echo "[$TIMESTAMP] INFO: Tailscale running, IP: $TAILSCALE_IP" >> $LOGFILE
EOF

    chmod +x /opt/admin/tailscale-monitor.sh
    
    # Create cron job for monitoring
    cat > /etc/cron.d/tailscale-monitor << EOF
# Tailscale monitoring
*/5 * * * * root /opt/admin/tailscale-monitor.sh
EOF
    
    log_success "Tailscale monitoring configured"
}

# Main script
case "$1" in
    "install")
        check_root
        install_tailscale
        create_service_config
        setup_firewall
        setup_admin_services
        setup_monitoring
        log_success "Tailscale installation completed"
        ;;
    "connect")
        check_root
        if [ -z "$2" ]; then
            log_error "Auth key is required: $0 connect <auth_key>"
            exit 1
        fi
        configure_tailscale "$2"
        ;;
    "generate-key")
        if [ -z "$2" ] || [ -z "$3" ]; then
            log_error "API key and tailnet are required: $0 generate-key <api_key> <tailnet>"
            exit 1
        fi
        generate_auth_key "$2" "$3"
        ;;
    "status")
        check_status
        ;;
    "disconnect")
        check_root
        disconnect
        ;;
    "remove")
        check_root
        remove_tailscale
        ;;
    "restart")
        check_root
        systemctl restart tailscaled
        tailscale up --accept-routes --accept-dns --hostname="$ADMIN_HOSTNAME"
        log_success "Tailscale restarted"
        ;;
    *)
        echo "Usage: $0 {install|connect <auth_key>|generate-key <api_key> <tailnet>|status|disconnect|remove|restart}"
        echo ""
        echo "Commands:"
        echo "  install                           - Install and configure Tailscale"
        echo "  connect <auth_key>               - Connect to Tailscale network"
        echo "  generate-key <api_key> <tailnet> - Generate auth key using API"
        echo "  status                           - Show Tailscale status"
        echo "  disconnect                       - Disconnect from Tailscale"
        echo "  remove                           - Remove Tailscale completely"
        echo "  restart                          - Restart Tailscale service"
        exit 1
        ;;
esac

