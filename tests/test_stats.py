# tests/test_stats.py - Statistics endpoint tests
class TestStats:
    """Test statistics API endpoint"""
    
    def test_get_stats_success(self, client, api_headers, db):
        """Test getting statistics for URL"""
        # Create URL and generate some clicks
        data = {
            'shortcode': 'stats-test',
            'destination': 'https://example.com'
        }
        client.post('/api/create', data=json.dumps(data), headers=api_headers)
        
        # Generate clicks
        client.get('/stats-test')
        client.get('/stats-test')
        
        # Get stats
        response = client.get('/api/stats/stats-test', headers=api_headers)
        
        assert response.status_code == 200
        result = response.get_json()
        
        assert result['shortcode'] == 'stats-test'
        assert result['destination'] == 'https://example.com'
        assert result['total_clicks'] == 2
        assert 'created' in result
        assert 'recent_clicks' in result
        assert len(result['recent_clicks']) == 2
    
    def test_get_stats_not_found(self, client, api_headers):
        """Test stats for non-existent URL"""
        response = client.get('/api/stats/nonexistent', headers=api_headers)
        assert response.status_code == 404
    
    def test_get_stats_unauthorized(self, client):
        """Test stats without API key"""
        response = client.get('/api/stats/test')
        assert response.status_code == 401
