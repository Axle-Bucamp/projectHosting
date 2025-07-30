import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.database import db
from src.routes.projects import projects_bp
from src.routes.store import store_bp
from src.routes.contact import contact_bp
from src.routes.admin import admin_bp
from src.routes.content import content_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'startup-secret-key-change-in-production'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(projects_bp, url_prefix='/api')
app.register_blueprint(store_bp, url_prefix='/api')
app.register_blueprint(contact_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(content_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'service': 'startup-backend-api'}, 200

@app.route('/', defaults={'path': ''})

@app.route('/metrics', methods=['GET'])
def metrics():
    """API metrics endpoint"""
    return {}, 200

@app.route('/health', methods=['GET'])
def health():
    """API health endpoint"""
    return {'status': 'healthy', 'service': 'startup-backend-api'}, 200

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
    app.run(host='0.0.0.0', port=5000, debug=True)

