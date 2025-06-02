# tests/test_integration.py - Integration tests
import pytest
import json
import time
from datetime import datetime, timedelta

@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete workflows"""
    
    def test_complete_url_lifecycle(self, client, api_headers, db):
        """Test complete URL creation, usage, and analytics workflow"""
        # 1. Create URL
        data = {
            'shortcode': 'lifecycle-test',
            'destination': 'https://example.com/test'
        }
        
        create_response = client.post('/api/create', 
                                    data=json.dumps(data), 
                                    headers=api_headers)
        assert create_response.status_code == 201
        
        # 2. Use URL multiple times
        for i in range(5):
            redirect_response = client.get('/lifecycle-test')
            assert redirect_response.status_code == 302
            time.sleep(0.1)  # Small delay between clicks
        
        # 3. Check stats
        stats_response = client.get('/api/stats/lifecycle-test', headers=api_headers)
        assert stats_response.status_code == 200
        
        stats = stats_response.get_json()
        assert stats['total_clicks'] == 5
        assert len(stats['recent_clicks']) == 5
        
        # 4. Verify chronological order of clicks
        timestamps = [click['timestamp'] for click in stats['recent_clicks']]
        # Should be in descending order (most recent first)
        for i in range(len(timestamps) - 1):
            assert timestamps[i] >= timestamps[i + 1]
    
    def test_multiple_urls_isolation(self, client, api_headers, db):
        """Test that multiple URLs don't interfere with each other"""
        urls = [
            {'shortcode': 'url1', 'destination': 'https://site1.com'},
            {'shortcode': 'url2', 'destination': 'https://site2.com'},
            {'shortcode': 'url3', 'destination': 'https://site3.com'}
        ]
        
        # Create multiple URLs
        for url_data in urls:
            response = client.post('/api/create', 
                                 data=json.dumps(url_data), 
                                 headers=api_headers)
            assert response.status_code == 201
        
        # Generate different click patterns
        client.get('/url1')  # 1 click
        for _ in range(3):   # 3 clicks
            client.get('/url2')
        for _ in range(2):   # 2 clicks
            client.get('/url3')
        
        # Verify isolated stats
        stats1 = client.get('/api/stats/url1', headers=api_headers).get_json()
        stats2 = client.get('/api/stats/url2', headers=api_headers).get_json()
        stats3 = client.get('/api/stats/url3', headers=api_headers).get_json()
        
        assert stats1['total_clicks'] == 1
        assert stats2['total_clicks'] == 3
        assert stats3['total_clicks'] == 2
        
        # Test list endpoint
        list_response = client.get('/api/list', headers=api_headers)
        assert list_response.status_code == 200
        
        url_list = list_response.get_json()['urls']
        assert len(url_list) == 3
