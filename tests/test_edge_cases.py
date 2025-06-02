# tests/test_edge_cases.py - Edge case and error condition tests
class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    @pytest.mark.parametrize("special_url", [
        "https://example.com/path?query=value&other=123",
        "https://example.com/path#fragment",
        "https://example.com/path?query=value#fragment",
        "https://sub.domain.example.com:8080/path",
        "https://example.com/file.pdf",
        "https://example.com/archive.tar.gz",
        "https://example.com/image.jpg",
    ])
    def test_special_destination_urls(self, client, api_headers, special_url):
        """Test various URL formats as destinations"""
        data = {
            'shortcode': f'test-{hash(special_url) % 1000}',
            'destination': special_url
        }
        
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        assert response.status_code == 201
        
        result = response.get_json()
        assert result['destination'] == special_url  # Preserved exactly
    
    @pytest.mark.parametrize("shortcode,expected", [
        ("Simple", "simple"),
        ("UPPERCASE", "uppercase"),
        ("MiXeD-CaSe", "mixed-case"),
        ("with-123", "with-123"),
        ("a", "a"),  # Single character
        ("123", "123"),  # Numbers only
    ])
    def test_shortcode_normalization(self, client, api_headers, shortcode, expected):
        """Test shortcode case normalization"""
        data = {
            'shortcode': shortcode,
            'destination': 'https://example.com'
        }
        
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        assert response.status_code == 201
        
        result = response.get_json()
        assert result['shortcode'] == expected
    
    def test_concurrent_access_simulation(self, client, api_headers, db):
        """Simulate concurrent access to same URL"""
        # Create URL
        data = {
            'shortcode': 'concurrent-test',
            'destination': 'https://example.com'
        }
        client.post('/api/create', data=json.dumps(data), headers=api_headers)
        
        # Simulate rapid concurrent clicks
        responses = []
        for _ in range(10):
            response = client.get('/concurrent-test')
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 302
        
        # Verify correct click count
        stats = client.get('/api/stats/concurrent-test', headers=api_headers).get_json()
        assert stats['total_clicks'] == 10
    
    def test_malformed_requests(self, client, api_headers):
        """Test handling of malformed requests"""
        # Invalid JSON
        response = client.post('/api/create', 
                             data='invalid json', 
                             headers=api_headers)
        assert response.status_code == 400
        
        # Missing headers
        response = client.post('/api/create', 
                             data=json.dumps({'shortcode': 'test'}))
        assert response.status_code == 401
        
        # Empty shortcode
        data = {'shortcode': '', 'destination': 'https://example.com'}
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        assert response.status_code == 400
