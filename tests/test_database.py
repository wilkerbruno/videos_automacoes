# tests/test_database.py
import pytest
import tempfile
import os
from models.database import DatabaseManager

class TestDatabaseManager:
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = DatabaseManager(db_path)
        yield db
        
        # Cleanup
        os.unlink(db_path)
    
    def test_save_and_get_post(self, db):
        """Test saving and retrieving posts"""
        post_data = {
            'id': 'test123',
            'title': 'Test Post',
            'description': 'Test Description',
            'category': 'entertainment',
            'hashtags': ['test', 'video'],
            'platforms': ['youtube', 'tiktok'],
            'status': 'draft'
        }
        
        # Save post
        assert db.save_post(post_data) is True
        
        # Retrieve post
        retrieved = db.get_post('test123')
        assert retrieved is not None
        assert retrieved['title'] == 'Test Post'
        assert retrieved['hashtags'] == ['test', 'video']
        assert retrieved['platforms'] == ['youtube', 'tiktok']
    
    def test_update_post(self, db):
        """Test updating posts"""
        # Save initial post
        post_data = {
            'id': 'test456',
            'title': 'Original Title',
            'status': 'draft'
        }
        db.save_post(post_data)
        
        # Update post
        updates = {
            'title': 'Updated Title',
            'status': 'posted'
        }
        assert db.update_post('test456', updates) is True
        
        # Verify update
        updated = db.get_post('test456')
        assert updated['title'] == 'Updated Title'
        assert updated['status'] == 'posted'
    
    def test_platform_credentials(self, db):
        """Test platform credential storage"""
        credentials = {
            'apiKey': 'test_key',
            'channelId': 'UC1234567890123456789012'
        }
        
        # Save credentials
        assert db.save_platform_credentials('youtube', credentials) is True
        
        # Retrieve credentials
        retrieved = db.get_platform_credentials('youtube')
        assert retrieved == credentials