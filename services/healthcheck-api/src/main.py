from flask import Flask, jsonify, request
from flask_cors import CORS
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import requests
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
        logging.FileHandler('/app/logs/healthcheck-api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for development

# Prometheus metrics
HEALTH_CHECK_COUNTER = Counter('health_checks_total', 'Total health checks performed', ['project', 'status'])
HEALTH_CHECK_DURATION = Histogram('health_check_duration_seconds', 'Health check duration', ['project'])
PROJECT_STATUS_GAUGE = Gauge('project_status', 'Project status (1=online, 0=offline)', ['project', 'url'])
RESPONSE_TIME_GAUGE = Gauge('project_response_time_seconds', 'Project response time', ['project'])
API_REQUEST_COUNTER = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])
UPTIME_GAUGE = Gauge('healthcheck_api_uptime_seconds', 'API uptime in seconds')

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
    
    # Create projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            status TEXT DEFAULT 'unknown',
            last_checked TIMESTAMP,
            response_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create health_checks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            status TEXT NOT NULL,
            response_time REAL,
            status_code INTEGER,
            error_message TEXT,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # Insert sample projects if table is empty
    cursor.execute('SELECT COUNT(*) FROM projects')
    if cursor.fetchone()[0] == 0:
        sample_projects = [
            ('E-commerce Platform', 'https://demo-ecommerce.example.com'),
            ('AI Chat Assistant', 'https://chat-ai.example.com'),
            ('Analytics Dashboard', 'https://analytics.example.com'),
            ('IoT Monitoring System', 'https://iot-monitor.example.com'),
            ('Blockchain Wallet', 'https://crypto-wallet.example.com'),
            ('Video Streaming Platform', 'https://video-stream.example.com')
        ]
        
        cursor.executemany(
            'INSERT INTO projects (name, url) VALUES (?, ?)',
            sample_projects
        )
        logger.info("Inserted sample projects into database")
    
    conn.commit()
    conn.close()

def check_url_health(url):
    """Check the health of a given URL"""
    try:
        start_time_check = time.time()
        response = requests.get(url, timeout=10, headers={'User-Agent': 'HealthCheck/1.0'})
        response_time = time.time() - start_time_check
        
        if response.status_code == 200:
            return {
                'status': 'online',
                'response_time': response_time,
                'status_code': response.status_code,
                'error_message': None
            }
        else:
            return {
                'status': 'offline',
                'response_time': response_time,
                'status_code': response.status_code,
                'error_message': f'HTTP {response.status_code}'
            }
    except requests.exceptions.Timeout:
        return {
            'status': 'offline',
            'response_time': None,
            'status_code': None,
            'error_message': 'Timeout'
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'offline',
            'response_time': None,
            'status_code': None,
            'error_message': 'Connection Error'
        }
    except Exception as e:
        return {
            'status': 'offline',
            'response_time': None,
            'status_code': None,
            'error_message': str(e)
        }

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Update uptime
    UPTIME_GAUGE.set(time.time() - start_time)
    
    # Record API metrics
    endpoint = request.endpoint or 'unknown'
    API_REQUEST_COUNTER.labels(
        endpoint=endpoint,
        method=request.method,
        status=response.status_code
    ).inc()
    
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
        cursor.execute('SELECT 1')
        conn.close()
        db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
        logger.error(f"Database health check failed: {str(e)}")
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'service': 'healthcheck-api',
        'uptime_seconds': time.time() - start_time,
        'checks': {
            'database': db_status
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health endpoint (legacy)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'healthcheck-api'
    })

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all projects with their current status"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT p.id, p.name, p.url, p.status, p.last_checked, p.response_time
        FROM projects p
        ORDER BY p.name
    ''')
    
    projects = []
    for row in cursor.fetchall():
        project_data = {
            'id': row[0],
            'name': row[1],
            'url': row[2],
            'status': row[3],
            'last_checked': row[4],
            'response_time': row[5]
        }
        projects.append(project_data)
        
        # Update Prometheus metrics
        status_value = 1 if row[3] == 'online' else 0
        PROJECT_STATUS_GAUGE.labels(project=row[1], url=row[2]).set(status_value)
        if row[5] is not None:
            RESPONSE_TIME_GAUGE.labels(project=row[1]).set(row[5])
    
    conn.close()
    return jsonify(projects)

@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'url' not in data:
        return jsonify({'error': 'Name and URL are required'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO projects (name, url) VALUES (?, ?)',
            (data['name'], data['url'])
        )
        project_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"Created new project: {data['name']} - {data['url']}")
        
        return jsonify({
            'id': project_id,
            'name': data['name'],
            'url': data['url'],
            'status': 'unknown',
            'created_at': datetime.now().isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        return jsonify({'error': 'Failed to create project'}), 500
    finally:
        conn.close()

@app.route('/api/projects/<int:project_id>/check', methods=['POST'])
def check_project(project_id):
    """Check the health of a specific project"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get project URL
    cursor.execute('SELECT name, url FROM projects WHERE id = ?', (project_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Project not found'}), 404
    
    name, url = result
    
    # Perform health check with metrics
    with HEALTH_CHECK_DURATION.labels(project=name).time():
        health_result = check_url_health(url)
    
    # Update Prometheus metrics
    HEALTH_CHECK_COUNTER.labels(project=name, status=health_result['status']).inc()
    status_value = 1 if health_result['status'] == 'online' else 0
    PROJECT_STATUS_GAUGE.labels(project=name, url=url).set(status_value)
    if health_result['response_time'] is not None:
        RESPONSE_TIME_GAUGE.labels(project=name).set(health_result['response_time'])
    
    # Update project status
    cursor.execute('''
        UPDATE projects 
        SET status = ?, last_checked = ?, response_time = ?
        WHERE id = ?
    ''', (
        health_result['status'],
        datetime.now().isoformat(),
        health_result['response_time'],
        project_id
    ))
    
    # Insert health check record
    cursor.execute('''
        INSERT INTO health_checks (project_id, status, response_time, status_code, error_message)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        project_id,
        health_result['status'],
        health_result['response_time'],
        health_result['status_code'],
        health_result['error_message']
    ))
    
    conn.commit()
    conn.close()
    
    logger.info(f"Health check for {name}: {health_result['status']}")
    
    return jsonify({
        'project_id': project_id,
        'name': name,
        'url': url,
        **health_result,
        'checked_at': datetime.now().isoformat()
    })

@app.route('/api/projects/check-all', methods=['POST'])
def check_all_projects():
    """Check the health of all projects"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get all projects
    cursor.execute('SELECT id, name, url FROM projects')
    projects = cursor.fetchall()
    
    results = []
    
    for project in projects:
        project_id, name, url = project
        
        # Perform health check with metrics
        with HEALTH_CHECK_DURATION.labels(project=name).time():
            health_result = check_url_health(url)
        
        # Update Prometheus metrics
        HEALTH_CHECK_COUNTER.labels(project=name, status=health_result['status']).inc()
        status_value = 1 if health_result['status'] == 'online' else 0
        PROJECT_STATUS_GAUGE.labels(project=name, url=url).set(status_value)
        if health_result['response_time'] is not None:
            RESPONSE_TIME_GAUGE.labels(project=name).set(health_result['response_time'])
        
        # Update project status
        cursor.execute('''
            UPDATE projects 
            SET status = ?, last_checked = ?, response_time = ?
            WHERE id = ?
        ''', (
            health_result['status'],
            datetime.now().isoformat(),
            health_result['response_time'],
            project_id
        ))
        
        # Insert health check record
        cursor.execute('''
            INSERT INTO health_checks (project_id, status, response_time, status_code, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            project_id,
            health_result['status'],
            health_result['response_time'],
            health_result['status_code'],
            health_result['error_message']
        ))
        
        results.append({
            'project_id': project_id,
            'name': name,
            'url': url,
            **health_result
        })
    
    conn.commit()
    conn.close()
    
    online_count = sum(1 for r in results if r['status'] == 'online')
    logger.info(f"Checked all projects: {online_count}/{len(results)} online")
    
    return jsonify({
        'checked_at': datetime.now().isoformat(),
        'total_projects': len(results),
        'online_projects': online_count,
        'results': results
    })

@app.route('/api/projects/<int:project_id>/history', methods=['GET'])
def get_project_history(project_id):
    """Get health check history for a specific project"""
    limit = request.args.get('limit', 50, type=int)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT status, response_time, status_code, error_message, checked_at
        FROM health_checks
        WHERE project_id = ?
        ORDER BY checked_at DESC
        LIMIT ?
    ''', (project_id, limit))
    
    history = []
    for row in cursor.fetchall():
        history.append({
            'status': row[0],
            'response_time': row[1],
            'status_code': row[2],
            'error_message': row[3],
            'checked_at': row[4]
        })
    
    conn.close()
    return jsonify(history)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall statistics"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Count projects by status
    cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM projects
        GROUP BY status
    ''')
    
    status_counts = {}
    for row in cursor.fetchall():
        status_counts[row[0]] = row[1]
    
    # Get total projects
    cursor.execute('SELECT COUNT(*) FROM projects')
    total_projects = cursor.fetchone()[0]
    
    # Get average response time
    cursor.execute('SELECT AVG(response_time) FROM projects WHERE response_time IS NOT NULL')
    avg_response_time = cursor.fetchone()[0]
    
    # Get uptime percentage
    uptime_percentage = (status_counts.get('online', 0) / total_projects * 100) if total_projects > 0 else 0
    
    conn.close()
    
    return jsonify({
        'total_projects': total_projects,
        'status_counts': status_counts,
        'average_response_time': avg_response_time,
        'uptime_percentage': uptime_percentage,
        'api_uptime': time.time() - start_time
    })

if __name__ == '__main__':
    # Initialize database
    init_db()
    logger.info("HealthCheck API starting up")
    
    # Run the app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

