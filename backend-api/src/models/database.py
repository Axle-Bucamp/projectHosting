from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(500), nullable=False)
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default='unknown')  # online, maintenance, offline
    technologies = db.Column(db.Text)  # JSON string of technologies
    category = db.Column(db.String(100))
    featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'image_url': self.image_url,
            'status': self.status,
            'technologies': self.technologies,
            'category': self.category,
            'featured': self.featured,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class StoreItem(db.Model):
    __tablename__ = 'store_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='EUR')
    category = db.Column(db.String(100))  # service, template, formation, support
    duration = db.Column(db.String(50))  # 2h, accès à vie, mensuel, etc.
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)
    popular = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(500))
    external_url = db.Column(db.String(500))  # Lien vers Gumroad, Patreon, etc.
    features = db.Column(db.Text)  # JSON string of features
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'currency': self.currency,
            'category': self.category,
            'duration': self.duration,
            'rating': self.rating,
            'reviews_count': self.reviews_count,
            'popular': self.popular,
            'image_url': self.image_url,
            'external_url': self.external_url,
            'features': self.features,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Contact(db.Model):
    __tablename__ = 'contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='new')  # new, read, replied, archived
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'company': self.company,
            'subject': self.subject,
            'message': self.message,
            'status': self.status,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ContentBlock(db.Model):
    __tablename__ = 'content_blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(100), nullable=False)  # home, about, etc.
    section = db.Column(db.String(100), nullable=False)  # hero, features, etc.
    key = db.Column(db.String(100), nullable=False)  # title, description, etc.
    value = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), default='text')  # text, html, json, image_url
    order_index = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'page': self.page,
            'section': self.section,
            'key': self.key,
            'value': self.value,
            'content_type': self.content_type,
            'order_index': self.order_index,
            'active': self.active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='admin')
    active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

