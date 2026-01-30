#!/usr/bin/env python3
"""
Comprehensive test suite for simplified cookie-only extraction.
Run this to verify the codebase works correctly after simplification.
"""

from extractor import extract_from_cookies, parse_cookies

print("="*70)
print("SIMPLIFIED COOKIE EXTRACTION - COMPREHENSIVE TEST")
print("="*70)

# Test 1: Basic JSESSIONID extraction
print("\n1. Testing JSESSIONID extraction...")
cookies = [{'name': 'JSESSIONID', 'value': 'ABC123XYZ'}]
result = extract_from_cookies(cookies)
assert result['jsessionid'] == 'ABC123XYZ', "JSESSIONID not extracted"
assert result['token'] is None, "Token should be None"
assert result['x-signavio-id'] is None, "x-signavio-id should be None"
print("   ✅ JSESSIONID extracted correctly")

# Test 2: Token extraction
print("\n2. Testing token extraction...")
cookies = [{'name': 'token', 'value': 'TOKEN123'}]
result = extract_from_cookies(cookies)
assert result['token'] == 'TOKEN123', "Token not extracted"
assert result['x-signavio-id'] == 'TOKEN123', "x-signavio-id should equal token"
print("   ✅ token: TOKEN123")
print("   ✅ x-signavio-id: TOKEN123 (same as token)")

# Test 3: Complete extraction (both cookies)
print("\n3. Testing complete extraction (both cookies)...")
cookies = [
    {'name': 'JSESSIONID', 'value': '195917C00ABC008DE3D2385BFF6368AA'},
    {'name': 'token', 'value': '6926521bd90b446ba607f87b642d4302'},
    {'name': 'other_cookie', 'value': 'ignored'},
]
result = extract_from_cookies(cookies)
assert result['jsessionid'] == '195917C00ABC008DE3D2385BFF6368AA', "JSESSIONID not extracted"
assert result['token'] == '6926521bd90b446ba607f87b642d4302', "Token not extracted"
assert result['x-signavio-id'] == '6926521bd90b446ba607f87b642d4302', "x-signavio-id should equal token"
print("   ✅ Both cookies extracted successfully")
print(f"      JSESSIONID: {result['jsessionid']}")
print(f"      token: {result['token']}")
print(f"      x-signavio-id: {result['x-signavio-id']} (same as token)")

# Test 4: Empty cookie list
print("\n4. Testing empty cookie list...")
result = extract_from_cookies([])
assert result['jsessionid'] is None
assert result['token'] is None
assert result['x-signavio-id'] is None
print("   ✅ Handles empty list correctly (all None)")

# Test 5: None input
print("\n5. Testing None input...")
result = extract_from_cookies(None)
assert result['jsessionid'] is None
assert result['token'] is None
assert result['x-signavio-id'] is None
print("   ✅ Handles None input correctly (all None)")

# Test 6: Cookies with no matches
print("\n6. Testing cookies with no authentication tokens...")
cookies = [
    {'name': 'random_cookie', 'value': 'value1'},
    {'name': 'another_one', 'value': 'value2'},
    {'name': '_ga', 'value': 'GA1.2.123456'},
]
result = extract_from_cookies(cookies)
assert result['jsessionid'] is None
assert result['token'] is None
assert result['x-signavio-id'] is None
print("   ✅ Correctly ignores non-authentication cookies")

# Test 7: Parse cookie string
print("\n7. Testing parse_cookies helper function...")
cookie_string = "JSESSIONID=ABC123; token=TOKEN456; other=value"
cookies = parse_cookies(cookie_string)
assert len(cookies) == 3
assert cookies[0] == {'name': 'JSESSIONID', 'value': 'ABC123'}
assert cookies[1] == {'name': 'token', 'value': 'TOKEN456'}
assert cookies[2] == {'name': 'other', 'value': 'value'}
print("   ✅ Cookie string parsing works correctly")

# Test 8: Cookie with equals in value
print("\n8. Testing cookie with equals sign in value...")
cookie_string = "data=key=value"
cookies = parse_cookies(cookie_string)
assert len(cookies) == 1
assert cookies[0]['name'] == 'data'
assert cookies[0]['value'] == 'key=value'
print("   ✅ Handles equals sign in value correctly")

print("\n" + "="*70)
print("ALL TESTS PASSED! ✅")
print("="*70)
print("\nSummary:")
print("- Cookie extraction works for JSESSIONID and token")
print("- token value is also used for x-signavio-id (same value)")
print("- Handles edge cases: empty lists, None, non-auth cookies")
print("- parse_cookies helper function works correctly")
print("- Code is ultra-simple and focused on just two cookies")
print("\nThe ultra-simplified codebase is ready for use!")