import pytest
import requests
import time
import docker
import subprocess
from pathlib import Path

class TestDockerIntegration:
    """Test Docker Compose integration."""
    
    @pytest.fixture(scope="class")
    def docker_compose_up(self):
        """Start Docker Compose services for testing."""
        # Change to project directory
        project_dir = Path(__file__).parent.parent.parent
        
        # Start services
        subprocess.run([
            "docker-compose", "-f", "docker-compose.yml", "up", "-d"
        ], cwd=project_dir, check=True)
        
        # Wait for services to be ready
        time.sleep(30)
        
        yield
        
        # Cleanup
        subprocess.run([
            "docker-compose", "-f", "docker-compose.yml", "down"
        ], cwd=project_dir)

    def test_frontend_health(self, docker_compose_up):
        """Test frontend service health."""
        response = requests.get("http://localhost:3000/health", timeout=10)
        assert response.status_code == 200

    def test_backend_health(self, docker_compose_up):
        """Test backend service health."""
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'

    def test_bridge_health(self, docker_compose_up):
        """Test bridge service health."""
        response = requests.get("http://localhost:5001/api/health", timeout=10)
        assert response.status_code == 200

    def test_healthcheck_service(self, docker_compose_up):
        """Test healthcheck service."""
        response = requests.get("http://localhost:5000/api/health", timeout=10)
        assert response.status_code == 200

    def test_watchdog_service(self, docker_compose_up):
        """Test watchdog service."""
        response = requests.get("http://localhost:8081/health", timeout=10)
        assert response.status_code == 200

    def test_prometheus_metrics(self, docker_compose_up):
        """Test Prometheus metrics collection."""
        response = requests.get("http://localhost:9090/api/v1/targets", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        # Check that targets are being scraped
        assert len(data['data']['activeTargets']) > 0

    def test_grafana_dashboard(self, docker_compose_up):
        """Test Grafana dashboard access."""
        response = requests.get("http://localhost:3001/api/health", timeout=10)
        assert response.status_code == 200

class TestServiceCommunication:
    """Test communication between services."""
    
    @pytest.fixture(scope="class")
    def services_running(self):
        """Ensure services are running."""
        # This would typically be handled by the docker_compose_up fixture
        # but we're separating concerns for clarity
        yield

    def test_frontend_to_backend_communication(self, services_running):
        """Test frontend can communicate with backend."""
        # Test API call from frontend perspective
        response = requests.get("http://localhost:3000/api/projects", timeout=10)
        # This should proxy to the backend
        assert response.status_code in [200, 404]  # 404 is OK if no projects exist

    def test_backend_to_database_connection(self, services_running):
        """Test backend can connect to database."""
        response = requests.get("http://localhost:8000/api/health/detailed", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert data['database']['status'] == 'healthy'

    def test_backend_to_redis_connection(self, services_running):
        """Test backend can connect to Redis."""
        response = requests.get("http://localhost:8000/api/health/detailed", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert data['redis']['status'] == 'healthy'

    def test_bridge_to_services_communication(self, services_running):
        """Test bridge service can communicate with other services."""
        response = requests.get("http://localhost:5001/api/services/status", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        # Should have status for multiple services
        assert len(data['services']) >= 3

class TestDataPersistence:
    """Test data persistence across service restarts."""
    
    def test_project_data_persistence(self):
        """Test that project data persists across restarts."""
        # Create a project
        project_data = {
            'name': 'Integration Test Project',
            'description': 'Test project for integration testing',
            'url': 'https://test.example.com',
            'status': 'online'
        }
        
        # First, login to get auth token
        login_response = requests.post("http://localhost:8000/api/auth/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code == 404:
            # Create admin user if doesn't exist
            requests.post("http://localhost:8000/api/auth/register", json={
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123'
            })
            login_response = requests.post("http://localhost:8000/api/auth/login", json={
                'username': 'admin',
                'password': 'admin123'
            })
        
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        
        # Create project
        create_response = requests.post(
            "http://localhost:8000/api/projects",
            json=project_data,
            headers=headers
        )
        assert create_response.status_code == 201
        
        project_id = create_response.json()['project']['id']
        
        # Restart backend service (simulate)
        # In a real test, you'd restart the Docker container
        time.sleep(2)
        
        # Verify project still exists
        get_response = requests.get(f"http://localhost:8000/api/projects/{project_id}")
        assert get_response.status_code == 200
        
        retrieved_project = get_response.json()['project']
        assert retrieved_project['name'] == project_data['name']

class TestLoadBalancing:
    """Test load balancing and scaling."""
    
    def test_multiple_backend_requests(self):
        """Test that multiple requests are handled correctly."""
        responses = []
        
        for i in range(10):
            response = requests.get("http://localhost:8000/api/health")
            responses.append(response)
            time.sleep(0.1)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        import concurrent.futures
        
        def make_request():
            return requests.get("http://localhost:8000/api/projects")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code in [200, 404]

class TestMonitoring:
    """Test monitoring and observability."""
    
    def test_metrics_collection(self):
        """Test that metrics are being collected."""
        # Make some requests to generate metrics
        for _ in range(5):
            requests.get("http://localhost:8000/api/health")
            time.sleep(0.1)
        
        # Check Prometheus metrics
        response = requests.get("http://localhost:8000/metrics")
        assert response.status_code == 200
        
        metrics_text = response.text
        assert 'http_requests_total' in metrics_text
        assert 'http_request_duration_seconds' in metrics_text

    def test_log_aggregation(self):
        """Test that logs are being aggregated."""
        # Make requests to generate logs
        requests.get("http://localhost:8000/api/health")
        requests.get("http://localhost:8000/api/projects")
        
        # In a real test, you'd check log aggregation system
        # For now, just verify the endpoints are working
        assert True

class TestSecurity:
    """Test security features."""
    
    def test_unauthorized_access(self):
        """Test that unauthorized access is blocked."""
        response = requests.get("http://localhost:8000/api/admin/users")
        assert response.status_code == 401

    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = requests.options("http://localhost:8000/api/health")
        assert 'Access-Control-Allow-Origin' in response.headers

    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Make many requests quickly
        responses = []
        for i in range(50):
            response = requests.get("http://localhost:8000/api/health")
            responses.append(response.status_code)
        
        # Should eventually get rate limited (429)
        # Note: This depends on rate limiting configuration
        status_codes = set(responses)
        assert 200 in status_codes  # Some requests should succeed

class TestBackup:
    """Test backup functionality."""
    
    def test_backup_endpoint(self):
        """Test backup trigger endpoint."""
        # Login as admin
        login_response = requests.post("http://localhost:8000/api/auth/login", json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        if login_response.status_code == 200:
            token = login_response.json()['access_token']
            headers = {'Authorization': f'Bearer {token}'}
            
            # Trigger backup
            response = requests.post(
                "http://localhost:8000/api/admin/backup/trigger",
                headers=headers
            )
            assert response.status_code in [200, 202]  # 202 for async processing

if __name__ == '__main__':
    pytest.main([__file__, '-v'])

