from flask import Blueprint, request, jsonify
from src.models.database import db, Contact
from datetime import datetime

contact_bp = Blueprint('contact', __name__)

@contact_bp.route('/contact', methods=['POST'])
def submit_contact():
    """Soumettre un formulaire de contact"""
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'success': False, 'error': f'Field {field} is required'}), 400
        
        # Validation de l'email (basique)
        email = data['email'].strip()
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        # Récupération des informations de la requête
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        user_agent = request.headers.get('User-Agent', '')
        
        contact = Contact(
            name=data['name'].strip(),
            email=email,
            company=data.get('company', '').strip(),
            subject=data.get('subject', '').strip(),
            message=data['message'].strip(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(contact)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.',
            'contact_id': contact.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@contact_bp.route('/contact', methods=['GET'])
def get_contacts():
    """Récupérer tous les messages de contact (admin seulement)"""
    try:
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
                'pages': contacts.pages,
                'has_next': contacts.has_next,
                'has_prev': contacts.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contact_bp.route('/contact/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Récupérer un message de contact spécifique"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        # Marquer comme lu si c'était nouveau
        if contact.status == 'new':
            contact.status = 'read'
            db.session.commit()
        
        return jsonify({
            'success': True,
            'contact': contact.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404

@contact_bp.route('/contact/<int:contact_id>/status', methods=['PUT'])
def update_contact_status(contact_id):
    """Mettre à jour le statut d'un message de contact"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        data = request.get_json()
        
        valid_statuses = ['new', 'read', 'replied', 'archived']
        new_status = data.get('status')
        
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'error': 'Invalid status'}), 400
        
        contact.status = new_status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'contact': contact.to_dict(),
            'message': f'Status updated to {new_status}'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@contact_bp.route('/contact/stats', methods=['GET'])
def get_contact_stats():
    """Récupérer les statistiques des messages de contact"""
    try:
        total_contacts = Contact.query.count()
        new_contacts = Contact.query.filter_by(status='new').count()
        read_contacts = Contact.query.filter_by(status='read').count()
        replied_contacts = Contact.query.filter_by(status='replied').count()
        archived_contacts = Contact.query.filter_by(status='archived').count()
        
        # Messages des 7 derniers jours
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_contacts = Contact.query.filter(Contact.created_at >= week_ago).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_contacts': total_contacts,
                'new_contacts': new_contacts,
                'read_contacts': read_contacts,
                'replied_contacts': replied_contacts,
                'archived_contacts': archived_contacts,
                'recent_contacts': recent_contacts
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

