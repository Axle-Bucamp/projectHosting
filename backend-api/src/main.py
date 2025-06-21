import os
import sys
import time
import logging
from datetime import datetime
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from src.models.database import db
from src.routes.projects import projects_bp
from src.routes.store import store_bp
from src.routes.contact import contact_bp
from src.routes.admin import admin_bp
from src.routes.content import content_bp

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/backend-api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'startup-secret-key-change-in-production')

# Enable CORS for all routes
CORS(app, origins="*")

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')
DATABASE_CONNECTIONS = Gauge('database_connections_active', 'Active database connections')
ERROR_COUNT = Counter('application_errors_total', 'Total application errors', ['type'])
UPTIME_GAUGE = Gauge('application_uptime_seconds', 'Application uptime in seconds')

# Track application start time
app_start_time = time.time()

# Middleware for metrics collection
@app.before_request
def before_request():
    request.start_time = time.time()
    ACTIVE_CONNECTIONS.inc()

@app.after_request
def after_request(response):
    # Record request metrics
    request_duration = time.time() - request.start_time
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown'
    ).observe(request_duration)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or 'unknown',
        status=response.status_code
    ).inc()
    
    ACTIVE_CONNECTIONS.dec()
    
    # Log request
    logger.info(f"{request.method} {request.path} - {response.status_code} - {request_duration:.3f}s")
    
    return response

@app.errorhandler(Exception)
def handle_exception(e):
    ERROR_COUNT.labels(type=type(e).__name__).inc()
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500

# Register blueprints
app.register_blueprint(projects_bp, url_prefix='/api')
app.register_blueprint(store_bp, url_prefix='/api')
app.register_blueprint(contact_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(content_bp, url_prefix='/api')

# Database configuration
database_url = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
db.init_app(app)

# Create tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        ERROR_COUNT.labels(type='database_init_error').inc()

@app.route('/api/health')
def health_check():
    """Enhanced health check with detailed status"""
    try:
        # Check database connection
        with app.app_context():
            db.session.execute('SELECT 1')
            db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
        ERROR_COUNT.labels(type='health_check_db_error').inc()
    
    # Update uptime metric
    uptime = time.time() - app_start_time
    UPTIME_GAUGE.set(uptime)
    
    health_data = {
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'service': 'startup-backend-api',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime_seconds': uptime,
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'checks': {
            'database': db_status,
            'memory': 'healthy',  # Could add actual memory check
            'disk': 'healthy'     # Could add actual disk check
        }
    }
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    return jsonify(health_data), status_code

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    try:
        # Update database connection count
        with app.app_context():
            # This is a simplified metric - in production you'd want actual connection pool stats
            DATABASE_CONNECTIONS.set(1)  # Placeholder
        
        return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
    except Exception as e:
        logger.error(f"Error generating metrics: {str(e)}")
        ERROR_COUNT.labels(type='metrics_error').inc()
        return "Error generating metrics", 500

@app.route('/api/logs')
def get_logs():
    """Get application logs for admin interface"""
    try:
        log_file = '/app/logs/backend-api.log'
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Return last 100 lines
                recent_logs = lines[-100:] if len(lines) > 100 else lines
                
                logs = []
                for line in recent_logs:
                    if line.strip():
                        parts = line.split(' - ', 3)
                        if len(parts) >= 4:
                            logs.append({
                                'timestamp': parts[0],
                                'logger': parts[1],
                                'level': parts[2],
                                'message': parts[3].strip()
                            })
                
                return jsonify({
                    'logs': logs,
                    'total': len(logs)
                })
        else:
            return jsonify({'logs': [], 'total': 0})
    except Exception as e:
        logger.error(f"Error reading logs: {str(e)}")
        return jsonify({'error': 'Failed to read logs'}), 500

@app.route('/api/system/info')
def system_info():
    """Get system information for monitoring"""
    try:
        import psutil
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'cpu_percent': cpu_percent,
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used
            },
            'disk': {
                'total': disk.total,
                'free': disk.free,
                'used': disk.used,
                'percent': (disk.used / disk.total) * 100
            },
            'uptime': time.time() - app_start_time,
            'process_count': len(psutil.pids())
        }
        
        return jsonify({'system_info': system_data})
    except ImportError:
        # psutil not available, return basic info
        return jsonify({
            'system_info': {
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': time.time() - app_start_time,
                'status': 'limited_metrics'
            }
        })
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        return jsonify({'error': 'Failed to get system info'}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    logger.info("Starting Backend API server")
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

