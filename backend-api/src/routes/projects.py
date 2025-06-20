from flask import Blueprint, request, jsonify
from src.models.database import db, Project
import json

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET'])
def get_projects():
    """Récupérer tous les projets"""
    try:
        projects = Project.query.all()
        return jsonify({
            'success': True,
            'projects': [project.to_dict() for project in projects],
            'total': len(projects)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """Récupérer un projet spécifique"""
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify({
            'success': True,
            'project': project.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@projects_bp.route('/projects', methods=['POST'])
def create_project():
    """Créer un nouveau projet"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'url']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Field {field} is required'}), 400
        
        # Traitement des technologies (conversion en JSON string)
        technologies = data.get('technologies', [])
        if isinstance(technologies, list):
            technologies = json.dumps(technologies)
        
        project = Project(
            name=data['name'],
            description=data.get('description', ''),
            url=data['url'],
            image_url=data.get('image_url', ''),
            status=data.get('status', 'unknown'),
            technologies=technologies,
            category=data.get('category', ''),
            featured=data.get('featured', False)
        )
        
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': 'Project created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """Mettre à jour un projet"""
    try:
        project = Project.query.get_or_404(project_id)
        data = request.get_json()
        
        # Mise à jour des champs
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'url' in data:
            project.url = data['url']
        if 'image_url' in data:
            project.image_url = data['image_url']
        if 'status' in data:
            project.status = data['status']
        if 'technologies' in data:
            technologies = data['technologies']
            if isinstance(technologies, list):
                technologies = json.dumps(technologies)
            project.technologies = technologies
        if 'category' in data:
            project.category = data['category']
        if 'featured' in data:
            project.featured = data['featured']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'message': 'Project updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """Supprimer un projet"""
    try:
        project = Project.query.get_or_404(project_id)
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Project deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@projects_bp.route('/projects/status', methods=['GET'])
def get_projects_status():
    """Récupérer les statistiques des projets"""
    try:
        total_projects = Project.query.count()
        online_projects = Project.query.filter_by(status='online').count()
        maintenance_projects = Project.query.filter_by(status='maintenance').count()
        offline_projects = Project.query.filter_by(status='offline').count()
        
        # Compter les technologies uniques
        projects = Project.query.all()
        all_technologies = set()
        for project in projects:
            if project.technologies:
                try:
                    techs = json.loads(project.technologies)
                    all_technologies.update(techs)
                except:
                    pass
        
        return jsonify({
            'success': True,
            'stats': {
                'total_projects': total_projects,
                'online_projects': online_projects,
                'maintenance_projects': maintenance_projects,
                'offline_projects': offline_projects,
                'total_technologies': len(all_technologies)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

