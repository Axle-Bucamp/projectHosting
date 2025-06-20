import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.database import Project, StoreItem, Contact, Content
from datetime import datetime

class TestProjectModel:
    """Test Project model functionality."""
    
    def test_project_creation(self):
        """Test creating a project instance."""
        project = Project(
            name="Test Project",
            description="A test project",
            status="online",
            url="https://test.com",
            technologies=["React", "Node.js"],
            category="web-app"
        )
        
        assert project.name == "Test Project"
        assert project.description == "A test project"
        assert project.status == "online"
        assert project.url == "https://test.com"
        assert "React" in project.technologies
        assert project.category == "web-app"
        assert project.created_at is not None

    def test_project_to_dict(self):
        """Test project serialization to dictionary."""
        project = Project(
            name="Test Project",
            description="A test project",
            status="online"
        )
        project.id = 1
        project.created_at = datetime.now()
        project.updated_at = datetime.now()
        
        project_dict = project.to_dict()
        
        assert project_dict['id'] == 1
        assert project_dict['name'] == "Test Project"
        assert project_dict['status'] == "online"
        assert 'created_at' in project_dict
        assert 'updated_at' in project_dict

    def test_project_status_validation(self):
        """Test project status validation."""
        valid_statuses = ['online', 'maintenance', 'offline']
        
        for status in valid_statuses:
            project = Project(name="Test", status=status)
            assert project.status == status

class TestStoreItemModel:
    """Test StoreItem model functionality."""
    
    def test_store_item_creation(self):
        """Test creating a store item instance."""
        item = StoreItem(
            name="Test Service",
            description="A test service",
            price=99.99,
            currency="EUR",
            category="service",
            features=["Feature 1", "Feature 2"]
        )
        
        assert item.name == "Test Service"
        assert item.price == 99.99
        assert item.currency == "EUR"
        assert item.category == "service"
        assert "Feature 1" in item.features

    def test_store_item_to_dict(self):
        """Test store item serialization to dictionary."""
        item = StoreItem(
            name="Test Service",
            description="A test service",
            price=99.99,
            currency="EUR"
        )
        item.id = 1
        item.created_at = datetime.now()
        
        item_dict = item.to_dict()
        
        assert item_dict['id'] == 1
        assert item_dict['name'] == "Test Service"
        assert item_dict['price'] == 99.99
        assert item_dict['currency'] == "EUR"

class TestContactModel:
    """Test Contact model functionality."""
    
    def test_contact_creation(self):
        """Test creating a contact instance."""
        contact = Contact(
            name="John Doe",
            email="john@example.com",
            company="Test Corp",
            subject="Test Subject",
            message="This is a test message"
        )
        
        assert contact.name == "John Doe"
        assert contact.email == "john@example.com"
        assert contact.company == "Test Corp"
        assert contact.subject == "Test Subject"
        assert contact.message == "This is a test message"
        assert contact.status == "new"

    def test_contact_to_dict(self):
        """Test contact serialization to dictionary."""
        contact = Contact(
            name="John Doe",
            email="john@example.com",
            message="Test message"
        )
        contact.id = 1
        contact.created_at = datetime.now()
        
        contact_dict = contact.to_dict()
        
        assert contact_dict['id'] == 1
        assert contact_dict['name'] == "John Doe"
        assert contact_dict['email'] == "john@example.com"
        assert contact_dict['status'] == "new"

class TestContentModel:
    """Test Content model functionality."""
    
    def test_content_creation(self):
        """Test creating a content instance."""
        content = Content(
            page="home",
            section="hero",
            content={
                "title": "Welcome",
                "subtitle": "To our site"
            }
        )
        
        assert content.page == "home"
        assert content.section == "hero"
        assert content.content["title"] == "Welcome"
        assert content.content["subtitle"] == "To our site"

    def test_content_to_dict(self):
        """Test content serialization to dictionary."""
        content = Content(
            page="home",
            section="hero",
            content={"title": "Welcome"}
        )
        content.id = 1
        content.created_at = datetime.now()
        content.updated_at = datetime.now()
        
        content_dict = content.to_dict()
        
        assert content_dict['id'] == 1
        assert content_dict['page'] == "home"
        assert content_dict['section'] == "hero"
        assert content_dict['content']['title'] == "Welcome"

if __name__ == '__main__':
    pytest.main([__file__])

