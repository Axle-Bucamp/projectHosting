from flask import Blueprint, request, jsonify
from src.models.database import db, StoreItem
import json

store_bp = Blueprint('store', __name__)

@store_bp.route('/store', methods=['GET'])
def get_store_items():
    """Récupérer tous les articles du store"""
    try:
        category = request.args.get('category')
        popular_only = request.args.get('popular', '').lower() == 'true'
        
        query = StoreItem.query
        
        if category:
            query = query.filter_by(category=category)
        
        if popular_only:
            query = query.filter_by(popular=True)
        
        items = query.order_by(StoreItem.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'items': [item.to_dict() for item in items],
            'total': len(items)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@store_bp.route('/store/<int:item_id>', methods=['GET'])
def get_store_item(item_id):
    """Récupérer un article spécifique du store"""
    try:
        item = StoreItem.query.get_or_404(item_id)
        return jsonify({
            'success': True,
            'item': item.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@store_bp.route('/store', methods=['POST'])
def create_store_item():
    """Créer un nouvel article dans le store"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Field {field} is required'}), 400
        
        # Traitement des features (conversion en JSON string)
        features = data.get('features', [])
        if isinstance(features, list):
            features = json.dumps(features)
        
        item = StoreItem(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            currency=data.get('currency', 'EUR'),
            category=data.get('category', 'service'),
            duration=data.get('duration', ''),
            rating=float(data.get('rating', 0.0)),
            reviews_count=int(data.get('reviews_count', 0)),
            popular=data.get('popular', False),
            image_url=data.get('image_url', ''),
            external_url=data.get('external_url', ''),
            features=features
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': item.to_dict(),
            'message': 'Store item created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@store_bp.route('/store/<int:item_id>', methods=['PUT'])
def update_store_item(item_id):
    """Mettre à jour un article du store"""
    try:
        item = StoreItem.query.get_or_404(item_id)
        data = request.get_json()
        
        # Mise à jour des champs
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'price' in data:
            item.price = float(data['price'])
        if 'currency' in data:
            item.currency = data['currency']
        if 'category' in data:
            item.category = data['category']
        if 'duration' in data:
            item.duration = data['duration']
        if 'rating' in data:
            item.rating = float(data['rating'])
        if 'reviews_count' in data:
            item.reviews_count = int(data['reviews_count'])
        if 'popular' in data:
            item.popular = data['popular']
        if 'image_url' in data:
            item.image_url = data['image_url']
        if 'external_url' in data:
            item.external_url = data['external_url']
        if 'features' in data:
            features = data['features']
            if isinstance(features, list):
                features = json.dumps(features)
            item.features = features
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'item': item.to_dict(),
            'message': 'Store item updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@store_bp.route('/store/<int:item_id>', methods=['DELETE'])
def delete_store_item(item_id):
    """Supprimer un article du store"""
    try:
        item = StoreItem.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Store item deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@store_bp.route('/store/categories', methods=['GET'])
def get_store_categories():
    """Récupérer les catégories disponibles"""
    try:
        categories = db.session.query(StoreItem.category).distinct().all()
        category_list = [cat[0] for cat in categories if cat[0]]
        
        return jsonify({
            'success': True,
            'categories': category_list
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@store_bp.route('/store/stats', methods=['GET'])
def get_store_stats():
    """Récupérer les statistiques du store"""
    try:
        total_items = StoreItem.query.count()
        popular_items = StoreItem.query.filter_by(popular=True).count()
        
        # Calcul de la note moyenne
        avg_rating = db.session.query(db.func.avg(StoreItem.rating)).scalar() or 0.0
        
        # Total des avis
        total_reviews = db.session.query(db.func.sum(StoreItem.reviews_count)).scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_items': total_items,
                'popular_items': popular_items,
                'average_rating': round(avg_rating, 1),
                'total_reviews': total_reviews
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

