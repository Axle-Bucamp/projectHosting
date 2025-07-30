from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import time
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for development

# Database setup
DATABASE = 'src/database/app.db'

def init_db():
    """Initialize the database with required tables"""
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
    
    conn.commit()
    conn.close()

def check_url_health(url):
    """Check the health of a given URL"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        response_time = time.time() - start_time
        
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

@app.route('/api/health', methods=['GET'])
def api_health():
    """API health endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'healthcheck-api'
    })

@app.route('/metrics', methods=['GET'])
def metrics():
    """API metrics endpoint"""
    return jsonify({})

@app.route('/health', methods=['GET'])
def health():
    """API health endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'healthcheck-api'
    }), 200

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
        projects.append({
            'id': row[0],
            'name': row[1],
            'url': row[2],
            'status': row[3],
            'last_checked': row[4],
            'response_time': row[5]
        })
    
    conn.close()
    return jsonify(projects)

@app.route('/api/projects/<int:project_id>/check', methods=['POST'])
def check_project(project_id):
    """Check the health of a specific project"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get project URL
    cursor.execute('SELECT url FROM projects WHERE id = ?', (project_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'Project not found'}), 404
    
    url = result[0]
    
    # Perform health check
    health_result = check_url_health(url)
    
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
    
    return jsonify({
        'project_id': project_id,
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
        
        # Perform health check
        health_result = check_url_health(url)
        
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
    
    return jsonify({
        'checked_at': datetime.now().isoformat(),
        'total_projects': len(results),
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
    
    conn.close()
    
    return jsonify({
        'total_projects': total_projects,
        'status_counts': status_counts,
        'average_response_time': avg_response_time,
        'uptime_percentage': (status_counts.get('online', 0) / total_projects * 100) if total_projects > 0 else 0
    })

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)

