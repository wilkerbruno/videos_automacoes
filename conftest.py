# conftest.py (pytest configuration)
import pytest
import asyncio
import tempfile
import os
from app import create_app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory for tests"""
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ['UPLOAD_FOLDER'] = temp_dir
        yield temp_dir

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [{
            "message": {
                "content": '{"optimized_title": "Test Title", "viral_score": 85}'
            }
        }]
    }