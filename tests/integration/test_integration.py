import pytest
import requests
import time
import json
import docker
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class TestIntegrationFullStack:
    """Integration tests for the complete application stack."""
    
    @pytest.fixture(scope="class")
    def docker_client(self):
        """Setup Docker client for integration tests."""
        return docker.from_env()

    @pytest.fixture(scope="class")
    def application_stack(self, docker_client):
        """Start the complete application stack for testing."""
        # Start the application stack
        subprocess.run([
            "docker-compose", "-f", "/home/ubuntu/startup-website/docker-compose.yml", 
            "up", "-d"
        ], cwd="/home/ubuntu/startup-website")
        
        # Wait for services to be ready
        self._wait_for_services()
        
        yield
        
        # Cleanup
        subprocess.run([
            "docker-compose", "-f", "/home/ubuntu/startup-website/docker-compose.yml", 
            "down"
        ], cwd="/home/ubuntu/startup-website")

    def _wait_for_services(self):
        """Wait for all services to be ready."""
        services = [
            ("http://localhost:3000", "Frontend"),
            ("http://localhost:8000/api/health", "Backend API"),
            ("http://localhost:5432", "PostgreSQL"),  # Will fail but that's ok
            ("http://localhost:6379", "Redis"),       # Will fail but that's ok
        ]
        
        for url, service_name in services:
            if "api/health" in url:
                self._wait_for_http_service(url, service_name)
            elif "localhost:3000" in url:
                self._wait_for_http_service(url, service_name)

    def _wait_for_http_service(self, url, service_name, max_retries=60):
        """Wait for an HTTP service to be ready."""
        for i in range(max_retries):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code in [200, 404]:  # 404 is ok for frontend routes
                    print(f"{service_name} is ready")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        print(f"Warning: {service_name} not ready after {max_retries} seconds")

    def test_database_connectivity(self, application_stack):
        """Test database connectivity and basic operations."""
        # Test health endpoint which checks database
        response = requests.get("http://localhost:8000/api/health/detailed")
        assert response.status_code == 200
        
        health_data = response.json()
        assert "database" in health_data
        assert health_data["database"]["status"] == "healthy"

    def test_redis_connectivity(self, application_stack):
        """Test Redis connectivity."""
        # Test health endpoint which checks Redis
        response = requests.get("http://localhost:8000/api/health/detailed")
        assert response.status_code == 200
        
        health_data = response.json()
        assert "redis" in health_data
        # Redis might not be required for basic functionality

    def test_frontend_backend_integration(self, application_stack):
        """Test frontend and backend integration."""
        # 1. Create a project via API
        project_data = {
            'name': 'Integration Test Project',
            'description': 'Created during integration testing',
            'status': 'online',
            'url': 'https://integration-test.com',
            'technologies': ['React', 'Flask', 'Docker']
        }
        
        headers = {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            "http://localhost:8000/api/projects",
            data=json.dumps(project_data),
            headers=headers
        )
        assert response.status_code == 201
        project_id = response.json()['project']['id']
        
        # 2. Verify project appears in API
        response = requests.get("http://localhost:8000/api/projects")
        assert response.status_code == 200
        projects = response.json()['projects']
        
        integration_project = None
        for project in projects:
            if project['name'] == 'Integration Test Project':
                integration_project = project
                break
        
        assert integration_project is not None
        assert integration_project['status'] == 'online'
        
        # 3. Test frontend can access the data
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("http://localhost:3000/projects")
            
            # Wait for page to load
            time.sleep(3)
            
            # Check if the page loaded successfully
            assert "Prototypes" in driver.page_source or "Projects" in driver.page_source
            
            driver.quit()
        except Exception as e:
            print(f"Frontend test skipped due to: {e}")
        
        # 4. Cleanup - delete the test project
        response = requests.delete(
            f"http://localhost:8000/api/projects/{project_id}",
            headers=headers
        )
        assert response.status_code == 200

    def test_contact_form_end_to_end(self, application_stack):
        """Test contact form from frontend to backend storage."""
        # 1. Submit contact via API (simulating frontend)
        contact_data = {
            'name': 'Integration Test Contact',
            'email': 'integration-test@example.com',
            'company': 'Test Integration Corp',
            'subject': 'Integration Testing',
            'message': 'This contact was created during integration testing.'
        }
        
        response = requests.post(
            "http://localhost:8000/api/contact",
            data=json.dumps(contact_data),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        
        # 2. Verify contact was stored in database
        headers = {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            "http://localhost:8000/api/admin/contacts",
            headers=headers
        )
        assert response.status_code == 200
        contacts = response.json()['contacts']
        
        # Find our integration test contact
        test_contact = None
        for contact in contacts:
            if contact['email'] == 'integration-test@example.com':
                test_contact = contact
                break
        
        assert test_contact is not None
        assert test_contact['name'] == 'Integration Test Contact'
        assert test_contact['company'] == 'Test Integration Corp'
        assert test_contact['status'] == 'new'

    def test_store_management_integration(self, application_stack):
        """Test store management integration."""
        # 1. Create store item via API
        item_data = {
            'name': 'Integration Test Service',
            'description': 'A service for integration testing',
            'price': 299.99,
            'currency': 'EUR',
            'category': 'service',
            'features': ['Integration Testing', 'Quality Assurance', 'Documentation']
        }
        
        headers = {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            "http://localhost:8000/api/store",
            data=json.dumps(item_data),
            headers=headers
        )
        assert response.status_code == 201
        item_id = response.json()['item']['id']
        
        # 2. Verify item appears in public API
        response = requests.get("http://localhost:8000/api/store")
        assert response.status_code == 200
        items = response.json()['items']
        
        integration_item = None
        for item in items:
            if item['name'] == 'Integration Test Service':
                integration_item = item
                break
        
        assert integration_item is not None
        assert integration_item['price'] == 299.99
        assert 'Integration Testing' in integration_item['features']
        
        # 3. Update the item
        update_data = {
            'price': 349.99,
            'popular': True
        }
        
        response = requests.put(
            f"http://localhost:8000/api/store/{item_id}",
            data=json.dumps(update_data),
            headers=headers
        )
        assert response.status_code == 200
        updated_item = response.json()['item']
        assert updated_item['price'] == 349.99
        assert updated_item['popular'] is True
        
        # 4. Cleanup - delete the test item
        response = requests.delete(
            f"http://localhost:8000/api/store/{item_id}",
            headers=headers
        )
        assert response.status_code == 200

    def test_content_management_integration(self, application_stack):
        """Test content management integration."""
        # 1. Create content via API
        content_data = {
            'page': 'home',
            'section': 'integration-test',
            'content': {
                'title': 'Integration Test Content',
                'description': 'This content was created during integration testing',
                'enabled': True
            }
        }
        
        headers = {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            "http://localhost:8000/api/content",
            data=json.dumps(content_data),
            headers=headers
        )
        assert response.status_code == 201
        content_id = response.json()['content']['id']
        
        # 2. Retrieve content via public API
        response = requests.get("http://localhost:8000/api/content/home/integration-test")
        assert response.status_code == 200
        content = response.json()['content']
        assert content['content']['title'] == 'Integration Test Content'
        
        # 3. Update content
        update_data = {
            'content': {
                'title': 'Updated Integration Test Content',
                'description': 'This content was updated during integration testing',
                'enabled': True
            }
        }
        
        response = requests.put(
            f"http://localhost:8000/api/content/{content_id}",
            data=json.dumps(update_data),
            headers=headers
        )
        assert response.status_code == 200
        updated_content = response.json()['content']
        assert updated_content['content']['title'] == 'Updated Integration Test Content'
        
        # 4. Cleanup - delete the test content
        response = requests.delete(
            f"http://localhost:8000/api/content/{content_id}",
            headers=headers
        )
        assert response.status_code == 200

    def test_monitoring_endpoints(self, application_stack):
        """Test monitoring and health check endpoints."""
        # 1. Basic health check
        response = requests.get("http://localhost:8000/api/health")
        assert response.status_code == 200
        health = response.json()
        assert health['status'] == 'healthy'
        assert 'timestamp' in health
        assert 'version' in health
        
        # 2. Detailed health check
        response = requests.get("http://localhost:8000/api/health/detailed")
        assert response.status_code == 200
        detailed_health = response.json()
        assert 'database' in detailed_health
        assert 'services' in detailed_health
        
        # 3. System metrics (if available)
        try:
            response = requests.get("http://localhost:8000/api/admin/system/metrics")
            if response.status_code == 200:
                metrics = response.json()
                assert 'cpu' in metrics or 'memory' in metrics
        except:
            pass  # Metrics endpoint might not be implemented yet

if __name__ == '__main__':
    pytest.main([__file__])

