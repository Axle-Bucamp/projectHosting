import pytest
import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestFunctionalAPI:
    """Functional tests for the complete API."""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Setup API client for functional tests."""
        # Wait for API to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.BASE_URL}/api/health")
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        else:
            pytest.fail("API not available after 30 seconds")
        
        return requests.Session()

    def test_complete_project_workflow(self, api_client):
        """Test complete project management workflow."""
        # 1. Get initial projects (should be empty or existing)
        response = api_client.get(f"{self.BASE_URL}/api/projects")
        assert response.status_code == 200
        initial_projects = response.json()['projects']
        initial_count = len(initial_projects)
        
        # 2. Create a new project
        project_data = {
            'name': 'Functional Test Project',
            'description': 'A project created during functional testing',
            'status': 'online',
            'url': 'https://functional-test.com',
            'technologies': ['React', 'Node.js', 'Docker'],
            'category': 'web-app'
        }
        
        headers = {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
        
        response = api_client.post(
            f"{self.BASE_URL}/api/projects",
            data=json.dumps(project_data),
            headers=headers
        )
        assert response.status_code == 201
        created_project = response.json()['project']
        project_id = created_project['id']
        
        # 3. Verify project was created
        response = api_client.get(f"{self.BASE_URL}/api/projects")
        assert response.status_code == 200
        projects = response.json()['projects']
        assert len(projects) == initial_count + 1
        
        # 4. Get specific project
        response = api_client.get(f"{self.BASE_URL}/api/projects/{project_id}")
        assert response.status_code == 200
        project = response.json()['project']
        assert project['name'] == 'Functional Test Project'
        assert project['status'] == 'online'
        
        # 5. Update project
        update_data = {
            'status': 'maintenance',
            'description': 'Updated during functional testing'
        }
        
        response = api_client.put(
            f"{self.BASE_URL}/api/projects/{project_id}",
            data=json.dumps(update_data),
            headers=headers
        )
        assert response.status_code == 200
        updated_project = response.json()['project']
        assert updated_project['status'] == 'maintenance'
        assert 'Updated during functional testing' in updated_project['description']
        
        # 6. Delete project
        response = api_client.delete(
            f"{self.BASE_URL}/api/projects/{project_id}",
            headers=headers
        )
        assert response.status_code == 200
        
        # 7. Verify project was deleted
        response = api_client.get(f"{self.BASE_URL}/api/projects/{project_id}")
        assert response.status_code == 404

    def test_complete_store_workflow(self, api_client):
        """Test complete store management workflow."""
        # 1. Get initial store items
        response = api_client.get(f"{self.BASE_URL}/api/store")
        assert response.status_code == 200
        initial_items = response.json()['items']
        initial_count = len(initial_items)
        
        # 2. Create a new store item
        item_data = {
            'name': 'Functional Test Service',
            'description': 'A service created during functional testing',
            'price': 149.99,
            'currency': 'EUR',
            'category': 'consultation',
            'features': ['Feature A', 'Feature B', 'Feature C'],
            'popular': True
        }
        
        headers = {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
        
        response = api_client.post(
            f"{self.BASE_URL}/api/store",
            data=json.dumps(item_data),
            headers=headers
        )
        assert response.status_code == 201
        created_item = response.json()['item']
        item_id = created_item['id']
        
        # 3. Verify item was created
        response = api_client.get(f"{self.BASE_URL}/api/store")
        assert response.status_code == 200
        items = response.json()['items']
        assert len(items) == initial_count + 1
        
        # 4. Update store item
        update_data = {
            'price': 199.99,
            'popular': False
        }
        
        response = api_client.put(
            f"{self.BASE_URL}/api/store/{item_id}",
            data=json.dumps(update_data),
            headers=headers
        )
        assert response.status_code == 200
        updated_item = response.json()['item']
        assert updated_item['price'] == 199.99
        assert updated_item['popular'] is False
        
        # 5. Delete store item
        response = api_client.delete(
            f"{self.BASE_URL}/api/store/{item_id}",
            headers=headers
        )
        assert response.status_code == 200

    def test_contact_form_workflow(self, api_client):
        """Test contact form submission workflow."""
        # 1. Submit contact form
        contact_data = {
            'name': 'Functional Test User',
            'email': 'functional-test@example.com',
            'company': 'Test Company Ltd',
            'subject': 'Functional Testing Inquiry',
            'message': 'This is a message submitted during functional testing.'
        }
        
        response = api_client.post(
            f"{self.BASE_URL}/api/contact",
            data=json.dumps(contact_data),
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code == 200
        result = response.json()
        assert result['success'] is True
        
        # 2. Verify contact was stored (admin endpoint)
        headers = {
            'Authorization': 'Bearer test-token',
            'Content-Type': 'application/json'
        }
        
        response = api_client.get(
            f"{self.BASE_URL}/api/admin/contacts",
            headers=headers
        )
        assert response.status_code == 200
        contacts = response.json()['contacts']
        
        # Find our test contact
        test_contact = None
        for contact in contacts:
            if contact['email'] == 'functional-test@example.com':
                test_contact = contact
                break
        
        assert test_contact is not None
        assert test_contact['name'] == 'Functional Test User'
        assert test_contact['subject'] == 'Functional Testing Inquiry'

class TestFunctionalFrontend:
    """Functional tests for the frontend application."""
    
    FRONTEND_URL = "http://localhost:3000"
    
    @pytest.fixture(scope="class")
    def driver(self):
        """Setup Selenium WebDriver for frontend tests."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        # Wait for frontend to be ready
        max_retries = 30
        for i in range(max_retries):
            try:
                driver.get(self.FRONTEND_URL)
                if "Startup" in driver.title:
                    break
            except Exception:
                time.sleep(1)
        else:
            pytest.fail("Frontend not available after 30 seconds")
        
        yield driver
        driver.quit()

    def test_homepage_navigation(self, driver):
        """Test homepage navigation and content."""
        driver.get(self.FRONTEND_URL)
        
        # Check page title
        assert "Startup" in driver.title
        
        # Check main heading
        heading = driver.find_element(By.TAG_NAME, "h1")
        assert "Solutions" in heading.text and "Cloud" in heading.text
        
        # Check navigation links
        nav_links = driver.find_elements(By.CSS_SELECTOR, "nav a")
        nav_texts = [link.text for link in nav_links]
        assert "Accueil" in nav_texts or "Home" in nav_texts
        assert "Prototypes" in nav_texts or "Projects" in nav_texts
        assert "Store" in nav_texts

    def test_projects_page(self, driver):
        """Test projects page functionality."""
        driver.get(f"{self.FRONTEND_URL}/projects")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Check page heading
        heading = driver.find_element(By.TAG_NAME, "h1")
        assert "Prototypes" in heading.text
        
        # Check if projects are loaded (or loading state)
        try:
            # Look for project cards or empty state
            projects_section = driver.find_element(By.CSS_SELECTOR, "[data-testid='projects-grid'], .grid")
            assert projects_section is not None
        except:
            # If no projects, should show empty state
            empty_state = driver.find_element(By.CSS_SELECTOR, ".text-center")
            assert empty_state is not None

    def test_store_page(self, driver):
        """Test store page functionality."""
        driver.get(f"{self.FRONTEND_URL}/store")
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        # Check page heading
        heading = driver.find_element(By.TAG_NAME, "h1")
        assert "Store" in heading.text
        
        # Check if store items are loaded (or loading state)
        try:
            # Look for store items or empty state
            store_section = driver.find_element(By.CSS_SELECTOR, "[data-testid='store-grid'], .grid")
            assert store_section is not None
        except:
            # If no items, should show empty state
            empty_state = driver.find_element(By.CSS_SELECTOR, ".text-center")
            assert empty_state is not None

    def test_contact_form(self, driver):
        """Test contact form functionality."""
        driver.get(self.FRONTEND_URL)
        
        # Scroll to contact form
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for contact form to be visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
        )
        
        # Fill out the form
        name_field = driver.find_element(By.CSS_SELECTOR, "input[name='name'], input[id='name']")
        email_field = driver.find_element(By.CSS_SELECTOR, "input[name='email'], input[id='email']")
        message_field = driver.find_element(By.CSS_SELECTOR, "textarea[name='message'], textarea[id='message']")
        
        name_field.send_keys("Functional Test User")
        email_field.send_keys("functional-test@example.com")
        message_field.send_keys("This is a functional test message.")
        
        # Submit the form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()
        
        # Wait for success message or form reset
        WebDriverWait(driver, 10).until(
            lambda d: "Message envoyé" in d.page_source or 
                     name_field.get_attribute("value") == ""
        )

if __name__ == '__main__':
    pytest.main([__file__])

