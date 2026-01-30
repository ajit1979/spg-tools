"""
Unit tests for extraction logic.
Tests pure parsing functions without browser dependencies.
"""

import pytest
from extractor import extract_from_cookies, parse_cookies


class TestExtractFromCookies:
    """Test cookie extraction logic."""
    
    def test_extract_jsessionid(self):
        cookies = [
            {'name': 'JSESSIONID', 'value': 'ABC123'},
            {'name': 'other', 'value': 'xyz'}
        ]
        result = extract_from_cookies(cookies)
        assert result['jsessionid'] == 'ABC123'
        
    def test_extract_token(self):
        cookies = [
            {'name': 'token', 'value': 'TOKEN123'},
        ]
        result = extract_from_cookies(cookies)
        assert result['token'] == 'TOKEN123'
        assert result['x-signavio-id'] == 'TOKEN123'  # Same value
        
    def test_extract_both(self):
        cookies = [
            {'name': 'JSESSIONID', 'value': 'ABC123'},
            {'name': 'token', 'value': 'TOKEN456'},
        ]
        result = extract_from_cookies(cookies)
        assert result['jsessionid'] == 'ABC123'
        assert result['token'] == 'TOKEN456'
        assert result['x-signavio-id'] == 'TOKEN456'  # Same as token
        
    def test_empty_cookies(self):
        result = extract_from_cookies([])
        assert result['jsessionid'] is None
        assert result['token'] is None
        assert result['x-signavio-id'] is None
        
    def test_none_cookies(self):
        result = extract_from_cookies(None)
        assert result['jsessionid'] is None
        
    def test_no_matching_cookies(self):
        cookies = [
            {'name': 'random', 'value': 'value1'},
            {'name': 'other', 'value': 'value2'},
        ]
        result = extract_from_cookies(cookies)
        assert result['jsessionid'] is None
        assert result['token'] is None


class TestExtractFromHeaders:
    """Test header extraction logic."""
    
    def test_extract_signavio_id_header(self):
        headers = {
          okies = parse_cookies(cookie_str)
        assert len(cookies) == 1
        assert cookies[0]['name'] == 'name'
        assert cookies[0]['value'] == 'value'
        
    def test_parse_multiple_cookies(self):
        cookie_str = 'session=abc123; user=john; token=xyz'
        cookies = parse_cookies(cookie_str)
        assert len(cookies) == 3
        assert cookies[0]['name'] == 'session'
        assert cookies[0]['value'] == 'abc123'
        assert cookies[1]['name'] == 'user'
        assert cookies[1]['value'] == 'john'
        
    def test_parse_cookies_with_spaces(self):
        cookie_str = 'name1 = value1 ; name2 = value2'
        cookies = parse_cookies(cookie_str)
        assert len(cookies) == 2
        assert cookies[0]['name'] == 'name1'
        assert cookies[0]['value'] == 'value1'
        
    def test_parse_empty_string(self):
        cookies = parse_cookies('')
        assert len(cookies) == 0
        
    def test_parse_none(self):
        cookies = parse_cookies(None)
        assert len(cookies) == 0
        
    def test_parse_cookie_with_equals_in_value(self):
        cookie_str = 'data=key=value'
        cookies = parse_cookies(cookie_str)
        assert len(cookies) == 1
        assert cookies[0]['name'] == 'data'
        assert cookies[0]['value'] == 'key=value'


class TestIntegration:
    """Integration tests combining multiple extraction methods."""
    
    def test_auto_detection_prefers_header(self):
        # Simulate having both header and cookies
        headers = {'x-signavio-id': 'header-id'}
        cookies = [{'name': 'signavio-id', 'value': 'cookie-id'}]
        
        header_result = extract_from_headers(headers)
        cookie_result = extract_from_cookies(cookies)
        
        # In auto mode, header should be preferred
        assert header_result['signavio_id'] == 'header-id'
        assert cookie_result['signavio_id'] == 'cookie-id'
        
    def test_fallback_to_cookies_when_no_header(self):
        headers = {}
        cookies = [
            {'name': 'JSESSIONID', 'value': 'session123'},
            {'name': 'auth_token', 'value': 'token456'}
        ]
        
        header_result = extract_from_headers(headers)
        cookie_result = extract_from_cookies(cookies)
        
        assert header_result['signavio_id'] is None
        assert cookie_result['jsessionid'] == 'session123'
        assert cookie_result['token'] == 'token456'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
