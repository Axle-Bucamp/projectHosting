# Tailscale Integration Documentation

## Overview

This setup provides secure access to admin interfaces through Tailscale VPN, ensuring that administrative functions are only accessible through encrypted tunnels.

## Architecture

```
Internet → Public Frontend (GCP Load Balancer)
    ↓
Tailscale Network → Admin Interface (Private)
    ↓
Admin Services:
- Admin Dashboard (Port 8080)
- Prometheus (Port 9090)
- Grafana (Port 3001)
```

## Setup Instructions

### 1. Install Tailscale

```bash
# Run the setup script
sudo ./scripts/tailscale-setup.sh install
```

### 2. Generate Auth Key

You need a Tailscale API key to generate auth keys programmatically:

```bash
# Generate auth key using Tailscale API
./scripts/tailscale-setup.sh generate-key <your_api_key> <your_tailnet>
```

### 3. Connect to Tailscale

```bash
# Connect using the generated auth key
sudo ./scripts/tailscale-setup.sh connect <auth_key>
```

### 4. Start Admin Services

```bash
# Start admin services with Tailscale
docker-compose -f docker-compose.admin.yml up -d
```

## Configuration

### Environment Variables

Create a `.env.admin` file:

```bash
# Tailscale configuration
TAILSCALE_AUTHKEY=your_auth_key_here
TAILSCALE_TAILNET=your_tailnet_name

# Admin credentials
GRAFANA_ADMIN_PASSWORD=secure_password_here
ADMIN_SECRET_KEY=your_admin_secret_key

# Database connection (if needed)
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Firewall Rules

The setup automatically configures firewall rules:

- Allow Tailscale traffic (UDP 41641)
- Allow admin services from Tailscale network (100.64.0.0/10)
- Deny all other access to admin ports

### Network Security

- Admin services are isolated in a separate Docker network
- Only accessible via Tailscale IP addresses
- All traffic is encrypted end-to-end
- No public exposure of admin interfaces

## Access URLs

Once connected to Tailscale, access admin services at:

- **Admin Dashboard**: `http://[tailscale-ip]:8080`
- **Prometheus**: `http://[tailscale-ip]:9090`
- **Grafana**: `http://[tailscale-ip]:3001`

To find your Tailscale IP:

```bash
tailscale ip -4
```

## Admin Interface Features

### Dashboard
- System overview and statistics
- Real-time monitoring
- Service health checks
- Recent activity logs

### Project Management
- Add/edit/delete projects
- Update project status
- Manage project images and URLs
- Technology stack management

### Store Management
- Product catalog management
- Pricing and descriptions
- Category organization
- Sales analytics

### Contact Management
- View contact form submissions
- Respond to inquiries
- Status tracking
- Export capabilities

### Content Management
- Dynamic content editing
- Page content updates
- Image management
- SEO optimization

### System Monitoring
- Server resource usage
- Application performance
- Database statistics
- Error tracking

## Security Best Practices

### 1. Access Control
- Use strong Tailscale auth keys
- Regularly rotate auth keys
- Monitor connected devices
- Remove unused devices

### 2. Authentication
- Change default admin passwords
- Use strong passwords
- Enable 2FA where possible
- Regular password rotation

### 3. Network Security
- Keep Tailscale updated
- Monitor network traffic
- Use ACLs for fine-grained access
- Regular security audits

### 4. Monitoring
- Monitor admin access logs
- Set up alerts for suspicious activity
- Regular backup of admin data
- Incident response procedures

## Troubleshooting

### Tailscale Connection Issues

```bash
# Check Tailscale status
sudo ./scripts/tailscale-setup.sh status

# Restart Tailscale
sudo ./scripts/tailscale-setup.sh restart

# Check logs
journalctl -u tailscaled -f
```

### Admin Services Issues

```bash
# Check admin services
docker-compose -f docker-compose.admin.yml ps

# View logs
docker-compose -f docker-compose.admin.yml logs -f

# Restart services
docker-compose -f docker-compose.admin.yml restart
```

### Network Connectivity

```bash
# Test Tailscale connectivity
ping [tailscale-ip]

# Test admin services
curl http://[tailscale-ip]:8080/health

# Check firewall rules
sudo ufw status
```

## Backup and Recovery

### Database Backup

```bash
# Backup admin data
docker-compose -f docker-compose.admin.yml exec backend-api python -c "
from src.routes.admin import admin_backup
admin_backup()
"
```

### Configuration Backup

```bash
# Backup Tailscale configuration
sudo cp -r /var/lib/tailscale /backup/tailscale-$(date +%Y%m%d)

# Backup Docker configurations
tar -czf admin-config-$(date +%Y%m%d).tar.gz docker-compose.admin.yml docker/nginx/admin-nginx.conf
```

## Monitoring and Alerts

### Prometheus Metrics

The admin setup includes monitoring for:

- Tailscale connection status
- Admin service availability
- Resource usage
- Security events

### Grafana Dashboards

Pre-configured dashboards for:

- System overview
- Network monitoring
- Security dashboard
- Performance metrics

### Alerting

Set up alerts for:

- Tailscale disconnection
- Admin service failures
- Unauthorized access attempts
- Resource exhaustion

## Maintenance

### Regular Tasks

1. **Weekly**:
   - Check Tailscale connectivity
   - Review admin access logs
   - Update admin passwords

2. **Monthly**:
   - Update Tailscale client
   - Rotate auth keys
   - Security audit

3. **Quarterly**:
   - Full system backup
   - Disaster recovery test
   - Security assessment

### Updates

```bash
# Update Tailscale
sudo apt update && sudo apt upgrade tailscale

# Update admin services
docker-compose -f docker-compose.admin.yml pull
docker-compose -f docker-compose.admin.yml up -d
```

## Support

For issues with:

- **Tailscale**: Check [Tailscale documentation](https://tailscale.com/kb/)
- **Admin Interface**: Check application logs and contact support
- **Infrastructure**: Review Terraform and Docker configurations

## Security Contacts

- **Security Issues**: Report immediately to security team
- **Access Issues**: Contact system administrator
- **Emergency**: Use emergency access procedures

