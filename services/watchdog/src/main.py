import os
import time
import requests
import logging
import json
from datetime import datetime
from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import threading
import schedule

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Prometheus metrics
service_health_gauge = Gauge('service_health_status', 'Health status of services', ['service'])
alert_counter = Counter('watchdog_alerts_total', 'Total alerts sent', ['type', 'service'])
check_duration = Histogram('watchdog_check_duration_seconds', 'Time spent checking services', ['service'])
system_uptime_gauge = Gauge('system_uptime_seconds', 'System uptime in seconds')

class WatchdogService:
    def __init__(self):
        self.services = {
            'frontend': {'url': 'http://frontend:80/health', 'critical': True},
            'backend-api': {'url': 'http://backend-api:8000/api/health', 'critical': True},
            'project-bridge': {'url': 'http://project-bridge:5001/health', 'critical': True},
            'healthcheck': {'url': 'http://healthcheck:5000/health', 'critical': False},
            'postgres': {'url': 'http://postgres:5432', 'critical': True, 'type': 'tcp'},
            'redis': {'url': 'http://redis:6379', 'critical': True, 'type': 'tcp'},
            'prometheus': {'url': 'http://prometheus:9090/-/healthy', 'critical': False},
            'grafana': {'url': 'http://grafana:3000/api/health', 'critical': False},
            'nginx': {'url': 'http://nginx:80/health', 'critical': True}
        }
        self.alert_webhook_url = os.getenv('ALERT_WEBHOOK_URL')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.prometheus_url = os.getenv('PROMETHEUS_URL', 'http://prometheus:9090')
        self.grafana_url = os.getenv('GRAFANA_URL', 'http://grafana:3000')
        self.check_interval = int(os.getenv('WATCHDOG_INTERVAL', 60))
        self.start_time = time.time()
        
    def check_service_health(self, service_name, config):
        """Check health of a specific service"""
        try:
            with check_duration.labels(service=service_name).time():
                if config.get('type') == 'tcp':
                    # TCP check for databases
                    import socket
                    host, port = config['url'].replace('http://', '').split(':')
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((host, int(port)))
                    sock.close()
                    is_healthy = result == 0
                else:
                    # HTTP check
                    response = requests.get(config['url'], timeout=10)
                    is_healthy = response.status_code == 200
                
                service_health_gauge.labels(service=service_name).set(1 if is_healthy else 0)
                
                if not is_healthy and config.get('critical', False):
                    self.send_alert(service_name, 'Service is down', 'critical')
                    alert_counter.labels(type='critical', service=service_name).inc()
                
                logger.info(f"Service {service_name}: {'healthy' if is_healthy else 'unhealthy'}")
                return is_healthy
                
        except Exception as e:
            logger.error(f"Error checking {service_name}: {str(e)}")
            service_health_gauge.labels(service=service_name).set(0)
            if config.get('critical', False):
                self.send_alert(service_name, f'Health check failed: {str(e)}', 'critical')
                alert_counter.labels(type='error', service=service_name).inc()
            return False
    
    def check_all_services(self):
        """Check health of all services"""
        logger.info("Starting health check cycle")
        results = {}
        
        for service_name, config in self.services.items():
            results[service_name] = self.check_service_health(service_name, config)
        
        # Update system uptime
        system_uptime_gauge.set(time.time() - self.start_time)
        
        # Check for system-wide issues
        critical_services_down = sum(1 for name, healthy in results.items() 
                                   if not healthy and self.services[name].get('critical', False))
        
        if critical_services_down >= 2:
            self.send_alert('system', f'{critical_services_down} critical services are down', 'emergency')
            alert_counter.labels(type='emergency', service='system').inc()
        
        logger.info(f"Health check completed. {sum(results.values())}/{len(results)} services healthy")
        return results
    
    def send_alert(self, service, message, severity='warning'):
        """Send alert to configured webhooks"""
        alert_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'service': service,
            'message': message,
            'severity': severity,
            'hostname': os.getenv('HOSTNAME', 'startup-server')
        }
        
        # Send to generic webhook
        if self.alert_webhook_url:
            try:
                requests.post(self.alert_webhook_url, json=alert_data, timeout=10)
                logger.info(f"Alert sent to webhook for {service}")
            except Exception as e:
                logger.error(f"Failed to send webhook alert: {str(e)}")
        
        # Send to Slack
        if self.slack_webhook_url:
            try:
                slack_message = {
                    'text': f"🚨 *{severity.upper()}* Alert",
                    'attachments': [{
                        'color': 'danger' if severity in ['critical', 'emergency'] else 'warning',
                        'fields': [
                            {'title': 'Service', 'value': service, 'short': True},
                            {'title': 'Message', 'value': message, 'short': False},
                            {'title': 'Time', 'value': alert_data['timestamp'], 'short': True}
                        ]
                    }]
                }
                requests.post(self.slack_webhook_url, json=slack_message, timeout=10)
                logger.info(f"Alert sent to Slack for {service}")
            except Exception as e:
                logger.error(f"Failed to send Slack alert: {str(e)}")
    
    def get_prometheus_metrics(self):
        """Get metrics from Prometheus"""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/query", 
                                  params={'query': 'up'}, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get Prometheus metrics: {str(e)}")
        return None
    
    def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info(f"Starting watchdog service with {self.check_interval}s interval")
        
        # Schedule regular health checks
        schedule.every(self.check_interval).seconds.do(self.check_all_services)
        
        # Schedule daily system report
        schedule.every().day.at("09:00").do(self.send_daily_report)
        
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    def send_daily_report(self):
        """Send daily system health report"""
        try:
            results = self.check_all_services()
            healthy_count = sum(results.values())
            total_count = len(results)
            
            report = {
                'date': datetime.utcnow().strftime('%Y-%m-%d'),
                'system_health': f"{healthy_count}/{total_count} services healthy",
                'uptime': f"{(time.time() - self.start_time) / 3600:.1f} hours",
                'services': results
            }
            
            if self.slack_webhook_url:
                slack_message = {
                    'text': f"📊 Daily System Health Report - {report['date']}",
                    'attachments': [{
                        'color': 'good' if healthy_count == total_count else 'warning',
                        'fields': [
                            {'title': 'System Health', 'value': report['system_health'], 'short': True},
                            {'title': 'Uptime', 'value': report['uptime'], 'short': True}
                        ]
                    }]
                }
                requests.post(self.slack_webhook_url, json=slack_message, timeout=10)
                
        except Exception as e:
            logger.error(f"Failed to send daily report: {str(e)}")

# Initialize watchdog service
watchdog = WatchdogService()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': time.time() - watchdog.start_time
    })

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/status')
def status():
    """Get current status of all services"""
    results = {}
    for service_name, config in watchdog.services.items():
        results[service_name] = watchdog.check_service_health(service_name, config)
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'services': results,
        'summary': {
            'total': len(results),
            'healthy': sum(results.values()),
            'unhealthy': len(results) - sum(results.values())
        }
    })

@app.route('/alerts', methods=['POST'])
def receive_alert():
    """Receive alerts from external systems"""
    try:
        alert_data = request.get_json()
        logger.info(f"Received external alert: {alert_data}")
        
        # Forward to configured webhooks
        if watchdog.alert_webhook_url:
            requests.post(watchdog.alert_webhook_url, json=alert_data, timeout=10)
        
        return jsonify({'status': 'received'}), 200
    except Exception as e:
        logger.error(f"Error processing alert: {str(e)}")
        return jsonify({'error': str(e)}), 500

def start_background_monitoring():
    """Start monitoring in background thread"""
    monitoring_thread = threading.Thread(target=watchdog.start_monitoring, daemon=True)
    monitoring_thread.start()

if __name__ == '__main__':
    # Start background monitoring
    start_background_monitoring()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8081, debug=False)

