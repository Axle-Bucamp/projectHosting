from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import requests
import json
import time
import logging
from datetime import datetime
import sqlite3
import os

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/project-bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for development

# Prometheus metrics
BRIDGE_REQUESTS_TOTAL = Counter('bridge_requests_total', 'Total bridge requests', ['service', 'method', 'status'])
BRIDGE_REQUEST_DURATION = Histogram('bridge_request_duration_seconds', 'Bridge request duration', ['service', 'method'])
BRIDGE_ACTIVE_CONNECTIONS = Gauge('bridge_active_connections', 'Active bridge connections')
SERVICE_STATUS_GAUGE = Gauge('bridge_service_status', 'Service status (1=enabled, 0=disabled)', ['service'])
BRIDGE_UPTIME_GAUGE = Gauge('bridge_uptime_seconds', 'Bridge uptime in seconds')
PROXY_ERRORS_TOTAL = Counter('bridge_proxy_errors_total', 'Total proxy errors', ['service', 'error_type'])

# Track start time
start_time = time.time()

# Database setup
DATABASE = '/app/database/app.db'

def init_db():
    """Initialize the database with required tables"""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create services table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            target_url TEXT NOT NULL,
            path_prefix TEXT NOT NULL,
            enabled BOOLEAN DEFAULT 1,
            auth_required BOOLEAN DEFAULT 0,
            rate_limit INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create request_logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER,
            method TEXT NOT NULL,
            path TEXT NOT NULL,
            status_code INTEGER,
            response_time REAL,
            user_agent TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services (id)
        )
    ''')
    
    # Insert sample services if table is empty
    cursor.execute('SELECT COUNT(*) FROM services')
    if cursor.fetchone()[0] == 0:
        sample_services = [
            ('Frontend App', 'web', 'http://frontend:80', '/app', 1, 0, 1000),
            ('Backend API', 'api', 'http://backend-api:8000', '/api', 1, 0, 1000),
            ('Admin Interface', 'web', 'http://admin-interface:80', '/admin', 1, 1, 500),
            ('Health Check API', 'api', 'http://healthcheck:5000', '/health', 1, 0, 200),
            ('Prometheus Metrics', 'monitoring', 'http://prometheus:9090', '/prometheus', 1, 1, 100),
            ('Grafana Dashboard', 'monitoring', 'http://grafana:3000', '/grafana', 1, 1, 100)
        ]
        
        cursor.executemany(
            'INSERT INTO services (name, type, target_url, path_prefix, enabled, auth_required, rate_limit) VALUES (?, ?, ?, ?, ?, ?, ?)',
            sample_services
        )
        logger.info("Inserted sample services into database")
    
    conn.commit()
    conn.close()

def log_request(service_id, method, path, status_code, response_time, user_agent, ip_address):
    """Log request details"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO request_logs (service_id, method, path, status_code, response_time, user_agent, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (service_id, method, path, status_code, response_time, user_agent, ip_address))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log request: {str(e)}")

def find_service_by_path(path):
    """Find service by path prefix"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, target_url, path_prefix, enabled, auth_required, rate_limit
        FROM services
        WHERE ? LIKE path_prefix || '%' AND enabled = 1
        ORDER BY LENGTH(path_prefix) DESC
        LIMIT 1
    ''', (path,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'name': result[1],
            'target_url': result[2],
            'path_prefix': result[3],
            'enabled': result[4],
            'auth_required': result[5],
            'rate_limit': result[6]
        }
    return None

@app.before_request
def before_request():
    request.start_time = time.time()
    BRIDGE_ACTIVE_CONNECTIONS.inc()

@app.after_request
def after_request(response):
    # Update uptime
    BRIDGE_UPTIME_GAUGE.set(time.time() - start_time)
    BRIDGE_ACTIVE_CONNECTIONS.dec()
    
    # Log request
    duration = time.time() - request.start_time
    logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")
    
    return response

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM services')
        service_count = cursor.fetchone()[0]
        conn.close()
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
        logger.error(f"Database health check failed: {str(e)}")
        service_count = 0
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'service': 'project-bridge',
        'uptime_seconds': time.time() - start_time,
        'registered_services': service_count,
        'checks': {
            'database': db_status
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    try:
        # Update service status metrics
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT name, enabled FROM services')
        for name, enabled in cursor.fetchall():
            SERVICE_STATUS_GAUGE.labels(service=name).set(1 if enabled else 0)
        conn.close()
        
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        logger.error(f"Error generating metrics: {str(e)}")
        return "Error generating metrics", 500

@app.route('/api/bridge/health', methods=['GET'])
def bridge_health():
    """Bridge service health endpoint (legacy)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'project-bridge'
    })

@app.route('/api/bridge/services', methods=['GET'])
def get_services():
    """Get all registered services"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, type, target_url, path_prefix, enabled, auth_required, rate_limit, created_at
        FROM services
        ORDER BY name
    ''')
    
    services = []
    for row in cursor.fetchall():
        service_data = {
            'id': row[0],
            'name': row[1],
            'type': row[2],
            'target_url': row[3],
            'path_prefix': row[4],
            'enabled': bool(row[5]),
            'auth_required': bool(row[6]),
            'rate_limit': row[7],
            'created_at': row[8]
        }
        services.append(service_data)
        
        # Update Prometheus metrics
        SERVICE_STATUS_GAUGE.labels(service=row[1]).set(1 if row[5] else 0)
    
    conn.close()
    return jsonify(services)

@app.route('/api/bridge/services', methods=['POST'])
def add_service():
    """Add a new service"""
    data = request.get_json()
    
    required_fields = ['name', 'type', 'target_url', 'path_prefix']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO services (name, type, target_url, path_prefix, enabled, auth_required, rate_limit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['type'],
            data['target_url'],
            data['path_prefix'],
            data.get('enabled', True),
            data.get('auth_required', False),
            data.get('rate_limit', 100)
        ))
        
        service_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"Added new service: {data['name']} -> {data['target_url']}")
        
        return jsonify({'id': service_id, 'message': 'Service added successfully'}), 201
        
    except Exception as e:
        logger.error(f"Error adding service: {str(e)}")
        return jsonify({'error': 'Failed to add service'}), 500
    finally:
        conn.close()

@app.route('/api/bridge/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    """Update a service"""
    data = request.get_json()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Check if service exists
        cursor.execute('SELECT name FROM services WHERE id = ?', (service_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Service not found'}), 404
        
        service_name = result[0]
        
        # Update service
        update_fields = []
        values = []
        
        for field in ['name', 'type', 'target_url', 'path_prefix', 'enabled', 'auth_required', 'rate_limit']:
            if field in data:
                update_fields.append(f'{field} = ?')
                values.append(data[field])
        
        if update_fields:
            values.append(service_id)
            cursor.execute(f'''
                UPDATE services 
                SET {', '.join(update_fields)}
                WHERE id = ?
            ''', values)
            
            conn.commit()
            logger.info(f"Updated service: {service_name}")
        
        return jsonify({'message': 'Service updated successfully'})
        
    except Exception as e:
        logger.error(f"Error updating service: {str(e)}")
        return jsonify({'error': 'Failed to update service'}), 500
    finally:
        conn.close()

@app.route('/api/bridge/stats', methods=['GET'])
def get_bridge_stats():
    """Get bridge statistics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Total services
        cursor.execute('SELECT COUNT(*) FROM services')
        total_services = cursor.fetchone()[0]
        
        # Active services
        cursor.execute('SELECT COUNT(*) FROM services WHERE enabled = 1')
        active_services = cursor.fetchone()[0]
        
        # Total requests (last 24 hours)
        cursor.execute('''
            SELECT COUNT(*) FROM request_logs 
            WHERE timestamp > datetime('now', '-1 day')
        ''')
        requests_24h = cursor.fetchone()[0]
        
        # Average response time (last 24 hours)
        cursor.execute('''
            SELECT AVG(response_time) FROM request_logs 
            WHERE timestamp > datetime('now', '-1 day') AND response_time IS NOT NULL
        ''')
        avg_response_time = cursor.fetchone()[0] or 0
        
        # Requests by service (last 24 hours)
        cursor.execute('''
            SELECT s.name, COUNT(r.id) as request_count, AVG(r.response_time) as avg_time
            FROM services s
            LEFT JOIN request_logs r ON s.id = r.service_id 
                AND r.timestamp > datetime('now', '-1 day')
            GROUP BY s.id, s.name
            ORDER BY request_count DESC
        ''')
        
        requests_by_service = []
        for row in cursor.fetchall():
            requests_by_service.append({
                'service': row[0],
                'requests': row[1],
                'avg_response_time': row[2] or 0
            })
        
        return jsonify({
            'total_services': total_services,
            'active_services': active_services,
            'requests_24h': requests_24h,
            'average_response_time': avg_response_time,
            'requests_by_service': requests_by_service,
            'uptime_seconds': time.time() - start_time
        })
        
    except Exception as e:
        logger.error(f"Error getting bridge stats: {str(e)}")
        return jsonify({'error': 'Failed to get statistics'}), 500
    finally:
        conn.close()

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(path):
    """Proxy requests to appropriate services"""
    request_start_time = time.time()
    
    # Find matching service
    service = find_service_by_path('/' + path)
    
    if not service:
        PROXY_ERRORS_TOTAL.labels(service='unknown', error_type='service_not_found').inc()
        return jsonify({'error': 'Service not found'}), 404
    
    service_name = service['name']
    
    # Build target URL
    remaining_path = path[len(service['path_prefix'].lstrip('/')):]
    target_url = service['target_url'].rstrip('/') + '/' + remaining_path.lstrip('/')
    
    try:
        # Record request metrics
        with BRIDGE_REQUEST_DURATION.labels(service=service_name, method=request.method).time():
            # Forward request
            response = requests.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers if k.lower() != 'host'},
                data=request.get_data(),
                params=request.args,
                timeout=30,
                allow_redirects=False
            )
        
        response_time = time.time() - request_start_time
        
        # Record metrics
        BRIDGE_REQUESTS_TOTAL.labels(
            service=service_name,
            method=request.method,
            status=response.status_code
        ).inc()
        
        # Log request
        log_request(
            service['id'],
            request.method,
            '/' + path,
            response.status_code,
            response_time,
            request.headers.get('User-Agent', ''),
            request.remote_addr
        )
        
        logger.info(f"Proxied {request.method} /{path} -> {target_url} ({response.status_code}, {response_time:.3f}s)")
        
        # Return response
        return response.content, response.status_code, dict(response.headers)
        
    except requests.exceptions.Timeout:
        response_time = time.time() - request_start_time
        PROXY_ERRORS_TOTAL.labels(service=service_name, error_type='timeout').inc()
        BRIDGE_REQUESTS_TOTAL.labels(service=service_name, method=request.method, status=504).inc()
        
        log_request(
            service['id'],
            request.method,
            '/' + path,
            504,
            response_time,
            request.headers.get('User-Agent', ''),
            request.remote_addr
        )
        
        logger.warning(f"Timeout proxying {request.method} /{path} -> {target_url}")
        return jsonify({'error': 'Gateway timeout'}), 504
        
    except requests.exceptions.ConnectionError:
        response_time = time.time() - request_start_time
        PROXY_ERRORS_TOTAL.labels(service=service_name, error_type='connection_error').inc()
        BRIDGE_REQUESTS_TOTAL.labels(service=service_name, method=request.method, status=502).inc()
        
        log_request(
            service['id'],
            request.method,
            '/' + path,
            502,
            response_time,
            request.headers.get('User-Agent', ''),
            request.remote_addr
        )
        
        logger.error(f"Connection error proxying {request.method} /{path} -> {target_url}")
        return jsonify({'error': 'Bad gateway'}), 502
        
    except Exception as e:
        response_time = time.time() - request_start_time
        PROXY_ERRORS_TOTAL.labels(service=service_name, error_type='internal_error').inc()
        BRIDGE_REQUESTS_TOTAL.labels(service=service_name, method=request.method, status=500).inc()
        
        log_request(
            service['id'],
            request.method,
            '/' + path,
            500,
            response_time,
            request.headers.get('User-Agent', ''),
            request.remote_addr
        )
        
        logger.error(f"Error proxying {request.method} /{path} -> {target_url}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    logger.info("Project Bridge starting up")
    
    # Run the app
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)

