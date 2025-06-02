# tests/test_api.py - API endpoint tests
import pytest
import json
from datetime import datetime

class TestCreateURL:
    """Test URL creation API endpoint"""
    
    def test_create_url_success(self, client, api_headers, db):
        """Test successful URL creation"""
        data = {
            'shortcode': 'test-url',
            'destination': 'https://example.com'
        }
        
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        
        assert response.status_code == 201
        result = response.get_json()
        
        assert result['shortcode'] == 'test-url'
        assert result['destination'] == 'https://example.com'
        assert 'short_url' in result
        assert 'created' in result
        
        # Verify data in Firestore
        doc = db.collection('urls').document('test-url').get()
        assert doc.exists
        data = doc.to_dict()
        assert data['destination'] == 'https://example.com'
        assert data['clicks'] == 0
    
    def test_create_url_case_insensitive(self, client, api_headers, db):
        """Test that shortcodes are converted to lowercase"""
        data = {
            'shortcode': 'TEST-URL',
            'destination': 'https://example.com'
        }
        
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        
        assert response.status_code == 201
        result = response.get_json()
        assert result['shortcode'] == 'test-url'  # Should be lowercase
        
        # Verify stored as lowercase
        doc = db.collection('urls').document('test-url').get()
        assert doc.exists
    
    def test_create_url_zip_detection(self, client, api_headers, db):
        """Test zip file detection"""
        data = {
            'shortcode': 'archive',
            'destination': 'https://example.com/files.zip'
        }
        
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        
        assert response.status_code == 201
        
        # Verify zip detection in Firestore
        doc = db.collection('urls').document('archive').get()
        data = doc.to_dict()
        assert data['is_zip'] is True
    
    def test_create_url_duplicate_shortcode(self, client, api_headers, db):
        """Test error when shortcode already exists"""
        # Create first URL
        data = {
            'shortcode': 'duplicate',
            'destination': 'https://example.com'
        }
        client.post('/api/create', data=json.dumps(data), headers=api_headers)
        
        # Try to create duplicate
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        
        assert response.status_code == 409
        result = response.get_json()
        assert 'already exists' in result['error']
    
    def test_create_url_invalid_api_key(self, client, db):
        """Test authentication with invalid API key"""
        headers = {
            'X-API-Key': 'wrong-key',
            'Content-Type': 'application/json'
        }
        data = {
            'shortcode': 'test',
            'destination': 'https://example.com'
        }
        
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=headers)
        
        assert response.status_code == 401
    
    def test_create_url_missing_data(self, client, api_headers):
        """Test validation of required fields"""
        # Missing destination
        data = {'shortcode': 'test'}
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        assert response.status_code == 400
        
        # Missing shortcode
        data = {'destination': 'https://example.com'}
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        assert response.status_code == 400
    
    @pytest.mark.parametrize("invalid_shortcode", [
        "test@code",  # @ symbol
        "test code",  # space
        "test.code",  # period
        "test_code",  # underscore
    ])
    def test_create_url_invalid_shortcode_format(self, client, api_headers, invalid_shortcode):
        """Test shortcode format validation"""
        data = {
            'shortcode': invalid_shortcode,
            'destination': 'https://example.com'
        }
        
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        
        assert response.status_code == 400
        result = response.get_json()
        assert 'letters, numbers, and hyphens' in result['error']

class TestRedirect:
    """Test URL redirection functionality"""
    
    def test_redirect_success(self, client, api_headers, db):
        """Test successful URL redirection"""
        # Create URL first
        data = {
            'shortcode': 'redirect-test',
            'destination': 'https://example.com'
        }
        client.post('/api/create', data=json.dumps(data), headers=api_headers)
        
        # Test redirect
        response = client.get('/redirect-test')
        
        assert response.status_code == 302
        assert response.location == 'https://example.com'
        
        # Verify click was tracked
        doc = db.collection('urls').document('redirect-test').get()
        data = doc.to_dict()
        assert data['clicks'] == 1
        
        # Verify click record in subcollection
        clicks = list(db.collection('urls').document('redirect-test')
                     .collection('clicks').stream())
        assert len(clicks) == 1
        click_data = clicks[0].to_dict()
        assert 'timestamp' in click_data
        assert 'ip' in click_data
    
    def test_redirect_case_insensitive(self, client, api_headers, db):
        """Test case-insensitive redirect lookup"""
        # Create lowercase URL
        data = {
            'shortcode': 'case-test',
            'destination': 'https://example.com'
        }
        client.post('/api/create', data=json.dumps(data), headers=api_headers)
        
        # Test uppercase access
        response = client.get('/CASE-TEST')
        assert response.status_code == 302
        assert response.location == 'https://example.com'
    
    def test_redirect_not_found(self, client):
        """Test 404 for non-existent shortcode"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_redirect_zip_file(self, client, api_headers, db):
        """Test zip file redirect shows download page"""
        # Create zip URL
        data = {
            'shortcode': 'zipfile',
            'destination': 'https://example.com/archive.zip'
        }
        client.post('/api/create', data=json.dumps(data), headers=api_headers)
        
        # Test redirect to zip
        response = client.get('/zipfile')
        
        assert response.status_code == 200  # Should show download page, not redirect
        assert b'download' in response.data.lower()
