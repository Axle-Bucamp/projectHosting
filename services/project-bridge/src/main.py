from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import requests
import json
from datetime import datetime
import sqlite3

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for development

# Database setup
DATABASE = 'src/database/app.db'

def init_db():
    """Initialize the database with required tables"""
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
            ('E-commerce API', 'api', 'https://api.ecommerce.example.com', '/api/ecommerce', 1, 0, 1000),
            ('AI Chat Service', 'api', 'https://chat-api.example.com', '/api/chat', 1, 1, 500),
            ('Analytics Service', 'api', 'https://analytics-api.example.com', '/api/analytics', 1, 1, 200),
            ('IoT Data Collector', 'api', 'https://iot-api.example.com', '/api/iot', 1, 0, 2000),
            ('Crypto Wallet API', 'api', 'https://wallet-api.example.com', '/api/wallet', 1, 1, 100),
            ('Video Processing', 'api', 'https://video-api.example.com', '/api/video', 1, 0, 50)
        ]
        
        cursor.executemany(
            'INSERT INTO services (name, type, target_url, path_prefix, enabled, auth_required, rate_limit) VALUES (?, ?, ?, ?, ?, ?, ?)',
            sample_services
        )
    
    conn.commit()
    conn.close()

def log_request(service_id, method, path, status_code, response_time, user_agent, ip_address):
    """Log request details"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO request_logs (service_id, method, path, status_code, response_time, user_agent, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (service_id, method, path, status_code, response_time, user_agent, ip_address))
    
    conn.commit()
    conn.close()

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

@app.route('/api/bridge/health', methods=['GET'])
def bridge_health():
    """Bridge service health endpoint"""
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
        services.append({
            'id': row[0],
            'name': row[1],
            'type': row[2],
            'target_url': row[3],
            'path_prefix': row[4],
            'enabled': bool(row[5]),
            'auth_required': bool(row[6]),
            'rate_limit': row[7],
            'created_at': row[8]
        })
    
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
    conn.close()
    
    return jsonify({'id': service_id, 'message': 'Service added successfully'}), 201

@app.route('/api/bridge/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    """Update a service"""
    data = request.get_json()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if service exists
    cursor.execute('SELECT id FROM services WHERE id = ?', (service_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Service not found'}), 404
    
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
    
    conn.close()
    return jsonify({'message': 'Service updated successfully'})

@app.route('/api/bridge/stats', methods=['GET'])
def get_bridge_stats():
    """Get bridge statistics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
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
    avg_response_time = cursor.fetchone()[0]
    
    # Requests by service (last 24 hours)
    cursor.execute('''
        SELECT s.name, COUNT(r.id) as request_count
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
            'requests': row[1]
        })
    
    conn.close()
    
    return jsonify({
        'total_services': total_services,
        'active_services': active_services,
        'requests_24h': requests_24h,
        'average_response_time': avg_response_time,
        'requests_by_service': requests_by_service
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    """API metrics endpoint"""
    return jsonify({})

@app.route('/health', methods=['GET'])
def health():
    """API health endpoint"""
    return {'status': 'healthy', 'service': 'startup-project-bridge'}, 200

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(path):
    """Proxy requests to appropriate services"""
    import time
    start_time = time.time()
    
    # Find matching service
    service = find_service_by_path('/' + path)
    
    if not service:
        return jsonify({'error': 'Service not found'}), 404
    
    # Build target URL
    remaining_path = path[len(service['path_prefix'].lstrip('/')):]
    target_url = service['target_url'].rstrip('/') + '/' + remaining_path.lstrip('/')
    
    try:
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
        
        response_time = time.time() - start_time
        
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
        
        # Return response
        return response.content, response.status_code, dict(response.headers)
        
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        log_request(
            service['id'],
            request.method,
            '/' + path,
            504,
            response_time,
            request.headers.get('User-Agent', ''),
            request.remote_addr
        )
        return jsonify({'error': 'Gateway timeout'}), 504
        
    except requests.exceptions.ConnectionError:
        response_time = time.time() - start_time
        log_request(
            service['id'],
            request.method,
            '/' + path,
            502,
            response_time,
            request.headers.get('User-Agent', ''),
            request.remote_addr
        )
        return jsonify({'error': 'Bad gateway'}), 502
        
    except Exception as e:
        response_time = time.time() - start_time
        log_request(
            service['id'],
            request.method,
            '/' + path,
            500,
            response_time,
            request.headers.get('User-Agent', ''),
            request.remote_addr
        )
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    app.run(host='0.0.0.0', port=5001, debug=True)

