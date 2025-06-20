#!/bin/bash

# Advanced Health Check Script
# Startup Website - Comprehensive Service Monitoring

set -e

# Configuration
APP_NAME="startup-website"
LOG_FILE="/opt/startup-website/logs/health-check.log"
ALERT_WEBHOOK="http://localhost:8000/api/webhooks/health"
SLACK_WEBHOOK="${SLACK_WEBHOOK_URL:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Health check results
HEALTH_STATUS=0
FAILED_SERVICES=()

# Send alert function
send_alert() {
    local severity=$1
    local message=$2
    local service=$3
    
    # Send to webhook
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -s -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"severity\": \"$severity\",
                \"message\": \"$message\",
                \"service\": \"$service\",
                \"timestamp\": \"$(date -Iseconds)\",
                \"hostname\": \"$(hostname)\"
            }" || true
    fi
    
    # Send to Slack
    if [ -n "$SLACK_WEBHOOK" ]; then
        local emoji="⚠️"
        [ "$severity" = "critical" ] && emoji="🚨"
        [ "$severity" = "warning" ] && emoji="⚠️"
        [ "$severity" = "info" ] && emoji="ℹ️"
        
        curl -s -X POST "$SLACK_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{
                \"text\": \"$emoji Health Check Alert\",
                \"attachments\": [{
                    \"color\": \"$([ "$severity" = "critical" ] && echo "danger" || echo "warning")\",
                    \"fields\": [
                        {\"title\": \"Severity\", \"value\": \"$severity\", \"short\": true},
                        {\"title\": \"Service\", \"value\": \"$service\", \"short\": true},
                        {\"title\": \"Message\", \"value\": \"$message\", \"short\": false},
                        {\"title\": \"Hostname\", \"value\": \"$(hostname)\", \"short\": true},
                        {\"title\": \"Time\", \"value\": \"$(date)\", \"short\": true}
                    ]
                }]
            }" || true
    fi
}

# Check HTTP endpoint
check_http() {
    local url=$1
    local service=$2
    local timeout=${3:-10}
    
    log "Checking HTTP endpoint: $url"
    
    if curl -sf --max-time "$timeout" "$url" > /dev/null; then
        success "$service HTTP endpoint is healthy"
        return 0
    else
        error "$service HTTP endpoint is down"
        FAILED_SERVICES+=("$service")
        send_alert "critical" "$service HTTP endpoint is not responding" "$service"
        return 1
    fi
}

# Check database connection
check_database() {
    log "Checking PostgreSQL database connection"
    
    if docker-compose exec -T postgres pg_isready -U startup -d startup_db > /dev/null 2>&1; then
        success "PostgreSQL database is healthy"
        return 0
    else
        error "PostgreSQL database is down"
        FAILED_SERVICES+=("postgres")
        send_alert "critical" "PostgreSQL database is not responding" "postgres"
        return 1
    fi
}

# Check Redis connection
check_redis() {
    log "Checking Redis connection"
    
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        success "Redis is healthy"
        return 0
    else
        error "Redis is down"
        FAILED_SERVICES+=("redis")
        send_alert "critical" "Redis is not responding" "redis"
        return 1
    fi
}

# Check Docker containers
check_containers() {
    log "Checking Docker containers status"
    
    local containers=(
        "startup-frontend"
        "startup-backend-api"
        "startup-postgres"
        "startup-redis"
        "startup-nginx"
        "startup-prometheus"
        "startup-grafana"
    )
    
    for container in "${containers[@]}"; do
        if docker ps --filter "name=$container" --filter "status=running" | grep -q "$container"; then
            success "Container $container is running"
        else
            error "Container $container is not running"
            FAILED_SERVICES+=("$container")
            send_alert "critical" "Container $container is not running" "$container"
            HEALTH_STATUS=1
        fi
    done
}

# Check disk space
check_disk_space() {
    log "Checking disk space"
    
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt 80 ]; then
        success "Disk space usage is healthy ($usage%)"
    elif [ "$usage" -lt 90 ]; then
        warning "Disk space usage is high ($usage%)"
        send_alert "warning" "Disk space usage is at $usage%" "system"
    else
        error "Disk space usage is critical ($usage%)"
        send_alert "critical" "Disk space usage is at $usage%" "system"
        HEALTH_STATUS=1
    fi
}

# Check memory usage
check_memory() {
    log "Checking memory usage"
    
    local usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    
    if [ "$usage" -lt 80 ]; then
        success "Memory usage is healthy ($usage%)"
    elif [ "$usage" -lt 90 ]; then
        warning "Memory usage is high ($usage%)"
        send_alert "warning" "Memory usage is at $usage%" "system"
    else
        error "Memory usage is critical ($usage%)"
        send_alert "critical" "Memory usage is at $usage%" "system"
        HEALTH_STATUS=1
    fi
}

# Check CPU usage
check_cpu() {
    log "Checking CPU usage"
    
    local usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    
    if (( $(echo "$usage < 80" | bc -l) )); then
        success "CPU usage is healthy ($usage%)"
    elif (( $(echo "$usage < 90" | bc -l) )); then
        warning "CPU usage is high ($usage%)"
        send_alert "warning" "CPU usage is at $usage%" "system"
    else
        error "CPU usage is critical ($usage%)"
        send_alert "critical" "CPU usage is at $usage%" "system"
        HEALTH_STATUS=1
    fi
}

# Check SSL certificate
check_ssl_certificate() {
    local domain=${1:-"localhost"}
    log "Checking SSL certificate for $domain"
    
    local expiry_date=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry_date" +%s)
    local current_epoch=$(date +%s)
    local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
    
    if [ "$days_until_expiry" -gt 30 ]; then
        success "SSL certificate is valid for $days_until_expiry days"
    elif [ "$days_until_expiry" -gt 7 ]; then
        warning "SSL certificate expires in $days_until_expiry days"
        send_alert "warning" "SSL certificate expires in $days_until_expiry days" "ssl"
    else
        error "SSL certificate expires in $days_until_expiry days"
        send_alert "critical" "SSL certificate expires in $days_until_expiry days" "ssl"
        HEALTH_STATUS=1
    fi
}

# Check log errors
check_log_errors() {
    log "Checking for recent errors in logs"
    
    local error_count=$(find /opt/startup-website/logs -name "*.log" -mtime -1 -exec grep -c "ERROR\|CRITICAL\|FATAL" {} + 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
    
    if [ "$error_count" -eq 0 ]; then
        success "No errors found in recent logs"
    elif [ "$error_count" -lt 10 ]; then
        warning "Found $error_count errors in recent logs"
        send_alert "warning" "Found $error_count errors in recent logs" "logs"
    else
        error "Found $error_count errors in recent logs"
        send_alert "critical" "Found $error_count errors in recent logs" "logs"
        HEALTH_STATUS=1
    fi
}

# Check backup status
check_backup_status() {
    log "Checking backup status"
    
    local backup_file="/opt/startup-website/backups/latest.tar.gz"
    
    if [ -f "$backup_file" ]; then
        local backup_age=$(( ($(date +%s) - $(stat -c %Y "$backup_file")) / 86400 ))
        
        if [ "$backup_age" -le 1 ]; then
            success "Backup is recent (${backup_age} days old)"
        elif [ "$backup_age" -le 3 ]; then
            warning "Backup is ${backup_age} days old"
            send_alert "warning" "Backup is ${backup_age} days old" "backup"
        else
            error "Backup is ${backup_age} days old"
            send_alert "critical" "Backup is ${backup_age} days old" "backup"
            HEALTH_STATUS=1
        fi
    else
        error "No backup file found"
        send_alert "critical" "No backup file found" "backup"
        HEALTH_STATUS=1
    fi
}

# Check external dependencies
check_external_dependencies() {
    log "Checking external dependencies"
    
    local dependencies=(
        "https://api.github.com"
        "https://registry-1.docker.io"
        "https://pypi.org"
    )
    
    for dep in "${dependencies[@]}"; do
        if curl -sf --max-time 10 "$dep" > /dev/null; then
            success "External dependency $dep is reachable"
        else
            warning "External dependency $dep is not reachable"
            send_alert "warning" "External dependency $dep is not reachable" "external"
        fi
    done
}

# Main health check function
main() {
    log "Starting comprehensive health check for $APP_NAME"
    
    # Change to application directory
    cd /opt/startup-website/source || exit 1
    
    # Run all health checks
    check_containers
    check_http "http://localhost:8000/api/health" "backend-api"
    check_http "http://localhost:3000" "frontend"
    check_http "http://localhost:5000/health" "healthcheck"
    check_database
    check_redis
    check_disk_space
    check_memory
    check_cpu
    check_log_errors
    check_backup_status
    check_external_dependencies
    
    # Summary
    if [ $HEALTH_STATUS -eq 0 ]; then
        success "All health checks passed"
        send_alert "info" "All health checks passed successfully" "system"
    else
        error "Health check failed. Failed services: ${FAILED_SERVICES[*]}"
        send_alert "critical" "Health check failed. Failed services: ${FAILED_SERVICES[*]}" "system"
    fi
    
    log "Health check completed with status: $HEALTH_STATUS"
    exit $HEALTH_STATUS
}

# Run main function
main "$@"

