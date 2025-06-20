from flask import Blueprint, request, jsonify
from src.models.database import db, ContentBlock
import json

content_bp = Blueprint('content', __name__)

@content_bp.route('/content/<page>', methods=['GET'])
def get_page_content(page):
    """Récupérer le contenu d'une page"""
    try:
        section = request.args.get('section')
        
        query = ContentBlock.query.filter_by(page=page, active=True)
        
        if section:
            query = query.filter_by(section=section)
        
        content_blocks = query.order_by(ContentBlock.order_index).all()
        
        # Organiser le contenu par section
        content = {}
        for block in content_blocks:
            if block.section not in content:
                content[block.section] = {}
            
            # Traiter le contenu selon le type
            value = block.value
            if block.content_type == 'json':
                try:
                    value = json.loads(block.value)
                except:
                    value = block.value
            
            content[block.section][block.key] = {
                'value': value,
                'type': block.content_type,
                'id': block.id
            }
        
        return jsonify({
            'success': True,
            'page': page,
            'content': content
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content', methods=['POST'])
def create_content_block():
    """Créer un nouveau bloc de contenu"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['page', 'section', 'key', 'value']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Field {field} is required'}), 400
        
        # Vérifier si le bloc existe déjà
        existing_block = ContentBlock.query.filter_by(
            page=data['page'],
            section=data['section'],
            key=data['key']
        ).first()
        
        if existing_block:
            return jsonify({'success': False, 'error': 'Content block already exists'}), 409
        
        # Traitement de la valeur selon le type
        value = data['value']
        content_type = data.get('content_type', 'text')
        
        if content_type == 'json' and isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        content_block = ContentBlock(
            page=data['page'],
            section=data['section'],
            key=data['key'],
            value=str(value),
            content_type=content_type,
            order_index=data.get('order_index', 0),
            active=data.get('active', True)
        )
        
        db.session.add(content_block)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'content_block': content_block.to_dict(),
            'message': 'Content block created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content/<int:block_id>', methods=['PUT'])
def update_content_block(block_id):
    """Mettre à jour un bloc de contenu"""
    try:
        content_block = ContentBlock.query.get_or_404(block_id)
        data = request.get_json()
        
        # Mise à jour des champs
        if 'value' in data:
            value = data['value']
            content_type = data.get('content_type', content_block.content_type)
            
            if content_type == 'json' and isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            content_block.value = str(value)
        
        if 'content_type' in data:
            content_block.content_type = data['content_type']
        if 'order_index' in data:
            content_block.order_index = data['order_index']
        if 'active' in data:
            content_block.active = data['active']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'content_block': content_block.to_dict(),
            'message': 'Content block updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content/<int:block_id>', methods=['DELETE'])
def delete_content_block(block_id):
    """Supprimer un bloc de contenu"""
    try:
        content_block = ContentBlock.query.get_or_404(block_id)
        db.session.delete(content_block)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Content block deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@content_bp.route('/content/pages', methods=['GET'])
def get_pages():
    """Récupérer la liste des pages disponibles"""
    try:
        pages = db.session.query(ContentBlock.page).distinct().all()
        page_list = [page[0] for page in pages]
        
        return jsonify({
            'success': True,
            'pages': page_list
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

