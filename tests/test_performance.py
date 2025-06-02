# tests/test_performance.py - Performance and load tests
@pytest.mark.slow
class TestPerformance:
    """Performance tests (marked as slow)"""
    
    def test_bulk_url_creation(self, client, api_headers, db):
        """Test creating many URLs quickly"""
        start_time = time.time()
        
        # Create 50 URLs
        for i in range(50):
            data = {
                'shortcode': f'bulk-{i:03d}',
                'destination': f'https://example.com/page{i}'
            }
            response = client.post('/api/create', 
                                 data=json.dumps(data), 
                                 headers=api_headers)
            assert response.status_code == 201
        
        duration = time.time() - start_time
        print(f"Created 50 URLs in {duration:.2f} seconds")
        
        # Verify all URLs exist
        list_response = client.get('/api/list', headers=api_headers)
        url_list = list_response.get_json()['urls']
        assert len(url_list) == 50
    
    def test_bulk_redirects(self, client, api_headers, db):
        """Test many redirects on single URL"""
        # Create URL
        data = {
            'shortcode': 'performance-test',
            'destination': 'https://example.com'
        }
        client.post('/api/create', data=json.dumps(data), headers=api_headers)
        
        start_time = time.time()
        
        # Generate 100 clicks
        for _ in range(100):
            response = client.get('/performance-test')
            assert response.status_code == 302
        
        duration = time.time() - start_time
        print(f"Processed 100 redirects in {duration:.2f} seconds")
        
        # Verify click tracking
        stats = client.get('/api/stats/performance-test', headers=api_headers).get_json()
        assert stats['total_clicks'] == 100
