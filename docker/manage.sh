#!/bin/bash

# Docker Compose Management Script
set -e

PROJECT_NAME="startup-website"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker and Docker Compose are installed
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Dependencies check passed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p docker/nginx/ssl
    mkdir -p docker/monitoring/grafana/{dashboards,datasources}
    mkdir -p backend-api/src/{database,backups}
    mkdir -p admin-interface
    
    log_success "Directories created"
}

# Generate SSL certificates (self-signed for development)
generate_ssl() {
    log_info "Generating SSL certificates..."
    
    if [ ! -f "docker/nginx/ssl/cert.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -keyout docker/nginx/ssl/key.pem \
            -out docker/nginx/ssl/cert.pem -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        log_success "SSL certificates generated"
    else
        log_info "SSL certificates already exist"
    fi
}

# Initialize environment variables
init_env() {
    log_info "Initializing environment variables..."
    
    if [ ! -f ".env" ]; then
        cat > .env << EOF
# Database
POSTGRES_DB=startup_db
POSTGRES_USER=startup_user
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Backend
FLASK_SECRET_KEY=$(openssl rand -base64 32)
ADMIN_SECRET_KEY=$(openssl rand -base64 32)

# Tailscale (set your auth key)
TAILSCALE_AUTHKEY=your_tailscale_auth_key_here

# Monitoring
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)
EOF
        log_success "Environment file created"
        log_warning "Please update .env file with your Tailscale auth key"
    else
        log_info "Environment file already exists"
    fi
}

# Build and start services
start_services() {
    log_info "Building and starting services..."
    
    docker-compose -p $PROJECT_NAME build
    docker-compose -p $PROJECT_NAME up -d
    
    log_success "Services started"
}

# Stop services
stop_services() {
    log_info "Stopping services..."
    
    docker-compose -p $PROJECT_NAME down
    
    log_success "Services stopped"
}

# Show service status
show_status() {
    log_info "Service status:"
    docker-compose -p $PROJECT_NAME ps
}

# Show logs
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose -p $PROJECT_NAME logs -f
    else
        docker-compose -p $PROJECT_NAME logs -f $service
    fi
}

# Backup database
backup_database() {
    log_info "Creating database backup..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="backup_${timestamp}.sql"
    
    docker-compose -p $PROJECT_NAME exec postgres pg_dump -U startup_user startup_db > $backup_file
    
    log_success "Database backup created: $backup_file"
}

# Restore database
restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        log_error "Please specify backup file"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    log_info "Restoring database from: $backup_file"
    
    docker-compose -p $PROJECT_NAME exec -T postgres psql -U startup_user startup_db < $backup_file
    
    log_success "Database restored"
}

# Update services
update_services() {
    log_info "Updating services..."
    
    docker-compose -p $PROJECT_NAME pull
    docker-compose -p $PROJECT_NAME build --no-cache
    docker-compose -p $PROJECT_NAME up -d
    
    log_success "Services updated"
}

# Clean up
cleanup() {
    log_info "Cleaning up..."
    
    docker-compose -p $PROJECT_NAME down -v --remove-orphans
    docker system prune -f
    
    log_success "Cleanup completed"
}

# Main script
case "$1" in
    "init")
        check_dependencies
        create_directories
        generate_ssl
        init_env
        log_success "Initialization completed"
        ;;
    "start")
        start_services
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        start_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs $2
        ;;
    "backup")
        backup_database
        ;;
    "restore")
        restore_database $2
        ;;
    "update")
        update_services
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {init|start|stop|restart|status|logs [service]|backup|restore [file]|update|cleanup}"
        echo ""
        echo "Commands:"
        echo "  init     - Initialize the project (run once)"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status"
        echo "  logs     - Show logs (optionally for specific service)"
        echo "  backup   - Create database backup"
        echo "  restore  - Restore database from backup"
        echo "  update   - Update and rebuild services"
        echo "  cleanup  - Stop services and clean up"
        exit 1
        ;;
esac

