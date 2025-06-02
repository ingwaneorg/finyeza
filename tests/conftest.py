# tests/conftest.py - pytest configuration and fixtures
import pytest
import os
import tempfile
import subprocess
import time
from google.cloud import firestore
from app import app as flask_app

@pytest.fixture(scope="session")
def firestore_emulator():
    """Start Firestore emulator for testing session"""
    # Start emulator in background
    process = subprocess.Popen([
        'gcloud', 'beta', 'emulators', 'firestore', 'start',
        '--host-port=localhost:8081',
        '--quiet'
    ])
    
    # Wait for emulator to start
    time.sleep(3)
    
    # Set environment variable for this session
    os.environ['FIRESTORE_EMULATOR_HOST'] = 'localhost:8081'
    
    yield
    
    # Cleanup: stop emulator
    process.terminate()
    process.wait()
    
    # Clean up environment
    if 'FIRESTORE_EMULATOR_HOST' in os.environ:
        del os.environ['FIRESTORE_EMULATOR_HOST']

@pytest.fixture
def db(firestore_emulator):
    """Provide clean Firestore database for each test"""
    # Create client connected to emulator
    client = firestore.Client(database='finyeza')
    
    # Clean up any existing test data
    collections = client.collections()
    for collection in collections:
        docs = collection.list_documents()
        for doc in docs:
            doc.delete()
    
    yield client
    
    # Cleanup after test
    collections = client.collections()
    for collection in collections:
        docs = collection.list_documents()
        for doc in docs:
            doc.delete()

@pytest.fixture
def app():
    """Create Flask app configured for testing"""
    flask_app.config['TESTING'] = True
    flask_app.config['API_KEY'] = 'test-api-key-123'
    
    # Set API key in environment for app to read
    os.environ['API_KEY'] = 'test-api-key-123'
    
    yield flask_app
    
    # Cleanup
    if 'API_KEY' in os.environ:
        del os.environ['API_KEY']

@pytest.fixture
def client(app):
    """Create test client for making HTTP requests"""
    return app.test_client()

@pytest.fixture
def api_headers():
    """Headers for authenticated API requests"""
    return {
        'X-API-Key': 'test-api-key-123',
        'Content-Type': 'application/json'
    }
