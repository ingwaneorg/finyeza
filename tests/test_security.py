# tests/test_security.py - Security tests
class TestSecurity:
    """Security-focused tests"""
    
    @pytest.mark.parametrize("malicious_input", [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "../../../etc/passwd",
        "'; DROP TABLE urls; --",
        "\x00\x01\x02",  # Null bytes
    ])
    def test_input_sanitization(self, client, api_headers, malicious_input):
        """Test handling of potentially malicious input"""
        data = {
            'shortcode': 'safe-code',
            'destination': malicious_input
        }
        
        response = client.post('/api/create', 
                             data=json.dumps(data), 
                             headers=api_headers)
        
        # Should either reject malicious input or store it safely
        if response.status_code == 201:
            # If accepted, verify it's stored exactly as provided
            result = response.get_json()
            assert result['destination'] == malicious_input
    
    def test_api_key_timing_attack_resistance(self, client):
        """Test that API key verification is timing-attack resistant"""
        wrong_keys = [
            "wrong",
            "test-api-key-12",  # Almost correct
            "test-api-key-123x",  # Almost correct
            "",
            "a" * 100,  # Very long
        ]
        
        times = []
        for key in wrong_keys:
            headers = {'X-API-Key': key, 'Content-Type': 'application/json'}
            data = {'shortcode': 'test', 'destination': 'https://example.com'}
            
            start = time.time()
            response = client.post('/api/create', 
                                 data=json.dumps(data), 
                                 headers=headers)
            duration = time.time() - start
            times.append(duration)
            
            assert response.status_code == 401
        
        # All timing should be relatively similar (constant-time comparison)
        max_time = max(times)
        min_time = min(times)
        # Allow for some variance but should be roughly constant
        assert max_time - min_time < 0.1  # 100ms tolerance
