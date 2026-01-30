"""
Pure extraction logic for parsing cookies.
This module contains no browser-specific code for easy unit testing.
"""


def extract_from_cookies(cookies):
    """
    Extract authentication tokens from cookies list.
    
    Args:
        cookies: List of cookie dicts with 'name' and 'value' keys
        
    Returns:
        Dict with extracted tokens: {jsessionid, token, x-signavio-id}
        Note: token and x-signavio-id have the same value
    """
    result = {
        'jsessionid': None,
        'token': None,
        'x-signavio-id': None
    }
    
    if not cookies:
        return result
    
    for cookie in cookies:
        name = cookie.get('name', '')
        value = cookie.get('value', '')
        
        if name == 'JSESSIONID':
            result['jsessionid'] = value
        elif name == 'token':
            result['token'] = value
            result['x-signavio-id'] = value  # Same value as token
            
    return result


def parse_cookies(cookie_string):
    """
    Parse a cookie string into a list of cookie dicts.
    
    Args:
        cookie_string: String like "name1=value1; name2=value2"
        
    Returns:
        List of dicts with 'name' and 'value' keys
    """
    cookies = []
    
    if not cookie_string:
        return cookies
    
    for part in cookie_string.split(';'):
        part = part.strip()
        if '=' in part:
            name, value = part.split('=', 1)
            cookies.append({'name': name.strip(), 'value': value.strip()})
            
    return cookies
