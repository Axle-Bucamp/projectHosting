import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app, db
from models.database import Project, StoreItem, Contact, Content
import json

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def auth_headers():
    """Create authentication headers for API requests."""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }

class TestHealthAPI:
    """Test health check endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

    def test_health_detailed(self, client):
        """Test detailed health check."""
        response = client.get('/api/health/detailed')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'database' in data
        assert 'redis' in data
        assert 'services' in data

class TestProjectsAPI:
    """Test projects management endpoints."""
    
    def test_get_projects_empty(self, client):
        """Test getting projects when none exist."""
        response = client.get('/api/projects')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['projects'] == []

    def test_create_project(self, client, auth_headers):
        """Test creating a new project."""
        project_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'status': 'online',
            'url': 'https://test.com',
            'technologies': ['React', 'Node.js'],
            'category': 'web-app'
        }
        
        response = client.post('/api/projects', 
                             data=json.dumps(project_data),
                             headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['project']['name'] == 'Test Project'

    def test_get_project_by_id(self, client, auth_headers):
        """Test getting a specific project by ID."""
        # First create a project
        project_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'status': 'online'
        }
        
        create_response = client.post('/api/projects',
                                    data=json.dumps(project_data),
                                    headers=auth_headers)
        project_id = json.loads(create_response.data)['project']['id']
        
        # Then get it
        response = client.get(f'/api/projects/{project_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['project']['name'] == 'Test Project'

    def test_update_project(self, client, auth_headers):
        """Test updating a project."""
        # Create project first
        project_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'status': 'online'
        }
        
        create_response = client.post('/api/projects',
                                    data=json.dumps(project_data),
                                    headers=auth_headers)
        project_id = json.loads(create_response.data)['project']['id']
        
        # Update it
        update_data = {
            'name': 'Updated Project',
            'status': 'maintenance'
        }
        
        response = client.put(f'/api/projects/{project_id}',
                            data=json.dumps(update_data),
                            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['project']['name'] == 'Updated Project'
        assert data['project']['status'] == 'maintenance'

    def test_delete_project(self, client, auth_headers):
        """Test deleting a project."""
        # Create project first
        project_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'status': 'online'
        }
        
        create_response = client.post('/api/projects',
                                    data=json.dumps(project_data),
                                    headers=auth_headers)
        project_id = json.loads(create_response.data)['project']['id']
        
        # Delete it
        response = client.delete(f'/api/projects/{project_id}',
                               headers=auth_headers)
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = client.get(f'/api/projects/{project_id}')
        assert get_response.status_code == 404

class TestStoreAPI:
    """Test store management endpoints."""
    
    def test_get_store_items_empty(self, client):
        """Test getting store items when none exist."""
        response = client.get('/api/store')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['items'] == []

    def test_create_store_item(self, client, auth_headers):
        """Test creating a new store item."""
        item_data = {
            'name': 'Test Service',
            'description': 'A test service',
            'price': 99.99,
            'currency': 'EUR',
            'category': 'service',
            'features': ['Feature 1', 'Feature 2']
        }
        
        response = client.post('/api/store',
                             data=json.dumps(item_data),
                             headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['item']['name'] == 'Test Service'
        assert data['item']['price'] == 99.99

class TestContactAPI:
    """Test contact form endpoints."""
    
    def test_submit_contact_form(self, client):
        """Test submitting a contact form."""
        contact_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'company': 'Test Corp',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        }
        
        response = client.post('/api/contact',
                             data=json.dumps(contact_data),
                             headers={'Content-Type': 'application/json'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'message' in data

    def test_get_contacts(self, client, auth_headers):
        """Test getting all contacts (admin only)."""
        # First submit a contact
        contact_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        
        client.post('/api/contact',
                   data=json.dumps(contact_data),
                   headers={'Content-Type': 'application/json'})
        
        # Then get all contacts
        response = client.get('/api/admin/contacts', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['contacts']) == 1
        assert data['contacts'][0]['name'] == 'John Doe'

class TestContentAPI:
    """Test content management endpoints."""
    
    def test_get_content_empty(self, client):
        """Test getting content when none exists."""
        response = client.get('/api/content/home')
        assert response.status_code == 404

    def test_create_content(self, client, auth_headers):
        """Test creating content."""
        content_data = {
            'page': 'home',
            'section': 'hero',
            'content': {
                'title': 'Welcome',
                'subtitle': 'To our site',
                'cta_text': 'Get Started'
            }
        }
        
        response = client.post('/api/content',
                             data=json.dumps(content_data),
                             headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['content']['page'] == 'home'

    def test_update_content(self, client, auth_headers):
        """Test updating content."""
        # Create content first
        content_data = {
            'page': 'home',
            'section': 'hero',
            'content': {'title': 'Welcome'}
        }
        
        create_response = client.post('/api/content',
                                    data=json.dumps(content_data),
                                    headers=auth_headers)
        content_id = json.loads(create_response.data)['content']['id']
        
        # Update it
        update_data = {
            'content': {'title': 'Updated Welcome'}
        }
        
        response = client.put(f'/api/content/{content_id}',
                            data=json.dumps(update_data),
                            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['content']['content']['title'] == 'Updated Welcome'

if __name__ == '__main__':
    pytest.main([__file__])

