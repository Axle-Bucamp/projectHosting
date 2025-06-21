import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import create_app
from models.database import db, Project, StoreItem, Contact, User

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers(client):
    """Create authentication headers for testing."""
    # Create a test user
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpassword123'
    })
    
    # Login to get token
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'testpassword123'
    })
    
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_endpoint(self, client):
        """Test the main health endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data

    def test_health_detailed(self, client):
        """Test detailed health endpoint."""
        response = client.get('/api/health/detailed')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'database' in data
        assert 'redis' in data
        assert 'services' in data

class TestProjectsAPI:
    """Test projects API endpoints."""
    
    def test_get_projects_empty(self, client):
        """Test getting projects when none exist."""
        response = client.get('/api/projects')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['projects'] == []
        assert data['total'] == 0

    def test_create_project(self, client, auth_headers):
        """Test creating a new project."""
        project_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'url': 'https://test.example.com',
            'status': 'online',
            'image_url': 'https://example.com/image.jpg'
        }
        
        response = client.post('/api/projects', 
                             json=project_data, 
                             headers=auth_headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['project']['name'] == project_data['name']
        assert data['project']['status'] == project_data['status']

    def test_get_project_by_id(self, client, auth_headers):
        """Test getting a specific project by ID."""
        # First create a project
        project_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'url': 'https://test.example.com',
            'status': 'online'
        }
        
        create_response = client.post('/api/projects', 
                                    json=project_data, 
                                    headers=auth_headers)
        project_id = create_response.get_json()['project']['id']
        
        # Then get it by ID
        response = client.get(f'/api/projects/{project_id}')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['project']['name'] == project_data['name']

    def test_update_project(self, client, auth_headers):
        """Test updating a project."""
        # Create a project first
        project_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'url': 'https://test.example.com',
            'status': 'online'
        }
        
        create_response = client.post('/api/projects', 
                                    json=project_data, 
                                    headers=auth_headers)
        project_id = create_response.get_json()['project']['id']
        
        # Update the project
        update_data = {
            'name': 'Updated Project',
            'status': 'maintenance'
        }
        
        response = client.put(f'/api/projects/{project_id}', 
                            json=update_data, 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['project']['name'] == update_data['name']
        assert data['project']['status'] == update_data['status']

    def test_delete_project(self, client, auth_headers):
        """Test deleting a project."""
        # Create a project first
        project_data = {
            'name': 'Test Project',
            'description': 'A test project',
            'url': 'https://test.example.com',
            'status': 'online'
        }
        
        create_response = client.post('/api/projects', 
                                    json=project_data, 
                                    headers=auth_headers)
        project_id = create_response.get_json()['project']['id']
        
        # Delete the project
        response = client.delete(f'/api/projects/{project_id}', 
                               headers=auth_headers)
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f'/api/projects/{project_id}')
        assert get_response.status_code == 404

class TestStoreAPI:
    """Test store API endpoints."""
    
    def test_get_store_items_empty(self, client):
        """Test getting store items when none exist."""
        response = client.get('/api/store')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['items'] == []
        assert data['total'] == 0

    def test_create_store_item(self, client, auth_headers):
        """Test creating a new store item."""
        item_data = {
            'name': 'Test Product',
            'description': 'A test product',
            'price': 99.99,
            'category': 'software',
            'image_url': 'https://example.com/product.jpg'
        }
        
        response = client.post('/api/store', 
                             json=item_data, 
                             headers=auth_headers)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['item']['name'] == item_data['name']
        assert data['item']['price'] == item_data['price']

class TestContactAPI:
    """Test contact API endpoints."""
    
    def test_submit_contact_form(self, client):
        """Test submitting a contact form."""
        contact_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        }
        
        response = client.post('/api/contact', json=contact_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['message'] == 'Contact form submitted successfully'

    def test_get_contacts(self, client, auth_headers):
        """Test getting contact submissions."""
        # Submit a contact form first
        contact_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message'
        }
        
        client.post('/api/contact', json=contact_data)
        
        # Get contacts
        response = client.get('/api/admin/contacts', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert len(data['contacts']) == 1
        assert data['contacts'][0]['name'] == contact_data['name']

class TestMetricsEndpoints:
    """Test Prometheus metrics endpoints."""
    
    def test_metrics_endpoint(self, client):
        """Test the metrics endpoint."""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert 'text/plain' in response.content_type
        
        # Check for basic metrics
        content = response.get_data(as_text=True)
        assert 'http_requests_total' in content
        assert 'http_request_duration_seconds' in content

class TestAuthenticationAPI:
    """Test authentication endpoints."""
    
    def test_register_user(self, client):
        """Test user registration."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepassword123'
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 201
        
        data = response.get_json()
        assert data['message'] == 'User created successfully'

    def test_login_user(self, client):
        """Test user login."""
        # Register a user first
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        client.post('/api/auth/register', json=user_data)
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'access_token' in data

    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get('/api/admin/users')
        assert response.status_code == 401

    def test_protected_endpoint_with_token(self, client, auth_headers):
        """Test accessing protected endpoint with valid token."""
        response = client.get('/api/admin/users', headers=auth_headers)
        assert response.status_code == 200

class TestImageUploadAPI:
    """Test image upload endpoints."""
    
    @patch('werkzeug.utils.secure_filename')
    @patch('os.path.exists')
    @patch('PIL.Image.open')
    def test_upload_image(self, mock_image_open, mock_exists, mock_secure_filename, client, auth_headers):
        """Test image upload."""
        mock_secure_filename.return_value = 'test.jpg'
        mock_exists.return_value = True
        
        # Mock PIL Image
        mock_image = Mock()
        mock_image.size = (800, 600)
        mock_image.format = 'JPEG'
        mock_image_open.return_value = mock_image
        
        data = {
            'image': (io.BytesIO(b'fake image data'), 'test.jpg')
        }
        
        response = client.post('/api/upload/image', 
                             data=data, 
                             headers=auth_headers,
                             content_type='multipart/form-data')
        
        # Note: This test would need more mocking for file system operations
        # In a real scenario, you'd mock the file saving operations

if __name__ == '__main__':
    pytest.main([__file__])

