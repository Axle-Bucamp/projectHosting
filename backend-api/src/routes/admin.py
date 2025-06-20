from flask import Blueprint, request, jsonify, session
from src.models.database import db, AdminUser, Project, StoreItem, Contact, ContentBlock
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

admin_bp = Blueprint('admin', __name__)

# Clé d'authentification simple (à remplacer par JWT en production)
ADMIN_SECRET_KEY = "admin-secret-key-change-in-production"

def require_admin_auth():
    """Vérifier l'authentification admin"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return False
    
    token = auth_header.split(' ')[1]
    return token == ADMIN_SECRET_KEY

@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Connexion administrateur"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        # Pour la démo, utiliser des identifiants par défaut
        if username == 'admin' and password == 'admin123':
            # Créer ou mettre à jour l'utilisateur admin
            admin_user = AdminUser.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = AdminUser(
                    username='admin',
                    email='admin@startup.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin_user)
            
            admin_user.last_login = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'token': ADMIN_SECRET_KEY,
                'user': admin_user.to_dict(),
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    """Tableau de bord administrateur"""
    try:
        if not require_admin_auth():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Statistiques générales
        total_projects = Project.query.count()
        online_projects = Project.query.filter_by(status='online').count()
        total_store_items = StoreItem.query.count()
        total_contacts = Contact.query.count()
        new_contacts = Contact.query.filter_by(status='new').count()
        
        # Projets récents
        recent_projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
        
        # Messages récents
        recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'dashboard': {
                'stats': {
                    'total_projects': total_projects,
                    'online_projects': online_projects,
                    'total_store_items': total_store_items,
                    'total_contacts': total_contacts,
                    'new_contacts': new_contacts
                },
                'recent_projects': [project.to_dict() for project in recent_projects],
                'recent_contacts': [contact.to_dict() for contact in recent_contacts]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/projects', methods=['GET'])
def admin_get_projects():
    """Gestion des projets (admin)"""
    try:
        if not require_admin_auth():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        projects = Project.query.order_by(Project.created_at.desc()).all()
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/store', methods=['GET'])
def admin_get_store():
    """Gestion du store (admin)"""
    try:
        if not require_admin_auth():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        items = StoreItem.query.order_by(StoreItem.created_at.desc()).all()
        return jsonify({
            'success': True,
            'items': [item.to_dict() for item in items]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/contacts', methods=['GET'])
def admin_get_contacts():
    """Gestion des contacts (admin)"""
    try:
        if not require_admin_auth():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        status_filter = request.args.get('status')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        query = Contact.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        contacts = query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'contacts': [contact.to_dict() for contact in contacts.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': contacts.total,
                'pages': contacts.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/content', methods=['GET'])
def admin_get_content():
    """Gestion du contenu (admin)"""
    try:
        if not require_admin_auth():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        page_filter = request.args.get('page')
        
        query = ContentBlock.query
        if page_filter:
            query = query.filter_by(page=page_filter)
        
        content_blocks = query.order_by(ContentBlock.page, ContentBlock.section, ContentBlock.order_index).all()
        
        return jsonify({
            'success': True,
            'content_blocks': [block.to_dict() for block in content_blocks]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/system/info', methods=['GET'])
def admin_system_info():
    """Informations système"""
    try:
        if not require_admin_auth():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        import os
        import psutil
        
        # Informations système
        system_info = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'uptime': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'system_info': system_info
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/backup', methods=['POST'])
def admin_backup():
    """Créer une sauvegarde de la base de données"""
    try:
        if not require_admin_auth():
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        import shutil
        import os
        from datetime import datetime
        
        # Chemin de la base de données
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
        backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
        
        # Créer le dossier de sauvegarde s'il n'existe pas
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nom du fichier de sauvegarde avec timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.db'
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copier la base de données
        shutil.copy2(db_path, backup_path)
        
        return jsonify({
            'success': True,
            'backup_file': backup_filename,
            'message': 'Backup created successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

