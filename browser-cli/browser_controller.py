"""
Browser controller using Playwright to manage Chromium sessions.
"""

from playwright.sync_api import sync_playwright
import re
import time
import os
import subprocess
from pathlib import Path


class BrowserController:
    """
    Controls browser interactions using Playwright.
    Opens Chromium in headed mode to allow user login via SSO.
    """
    
    def __init__(self, headless=False, timeout=300, browser_type='light'):
        """
        Initialize browser controller.

        Args:
            headless: Run browser in headless mode (False for SSO login)
            timeout: Timeout in seconds for operations
            browser_type: 'light' (Chromium) or 'full' (Chrome)
        """
        self.headless = headless
        self.timeout = timeout  # Keep in seconds for polling loop
        self.browser_type = browser_type.lower()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.user_info = {}
        
    def __enter__(self):
        """Context manager entry."""
        # Ensure browsers are installed and set environment
        self._ensure_browsers_installed()
        self._set_browser_path_env()
        
        self.playwright = sync_playwright().start()
        
        # Select browser type
        browser = self.playwright.chromium
        launch_kwargs = {
            'headless': self.headless
        }
        
        # For full Chrome, try to use installed Chrome
        if self.browser_type == 'full':
            print("Using Google Chrome browser (full)")
            try:
                launch_kwargs['channel'] = 'chrome'
            except:
                print("Chrome channel not available, using Chromium")
        else:
            print("Using Chromium browser (light)")
        
        # Launch browser and create context
        self.browser = browser.launch(**launch_kwargs)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()
        
        return self
    
    def _set_browser_path_env(self):
        """Set PLAYWRIGHT_BROWSERS_PATH to user's cache directory."""
        # macOS uses ~/Library/Caches, Linux uses ~/.cache
        if os.uname().sysname == 'Darwin':
            browsers_path = Path.home() / 'Library' / 'Caches' / 'ms-playwright'
        else:
            browsers_path = Path.home() / '.cache' / 'ms-playwright'
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(browsers_path)
    
    def _ensure_browsers_installed(self):
        """Ensure Playwright browsers are installed."""
        try:
            # Check if browsers are already installed
            if os.uname().sysname == 'Darwin':
                browsers_path = Path.home() / 'Library' / 'Caches' / 'ms-playwright'
            else:
                browsers_path = Path.home() / '.cache' / 'ms-playwright'
            if browsers_path.exists() and list(browsers_path.glob('chromium-*')):
                return
            
            # Install browsers
            print("Installing Playwright browsers...")
            subprocess.run(
                ['playwright', 'install', 'chromium'],
                check=True,
                capture_output=True
            )
            print("Browsers installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not auto-install browsers: {e}")
            print("Please run: playwright install chromium")
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
                
    def _capture_user_info_from_response(self, response):
        """Parse /p/user/{id} JSON response and cache user details from rel=info."""
        try:
            if response.status != 200:
                return

            # Accept /p/user/{id} with optional query string.
            if not re.search(r'/p/user/[^/?#]+(?:[?#].*)?$', response.url):
                return

            content_type = response.headers.get('content-type', '').lower()
            if 'json' not in content_type:
                return

            payload = response.json()
            if not isinstance(payload, list):
                return

            info_item = next(
                (item for item in payload if isinstance(item, dict) and item.get('rel') == 'info'),
                None,
            )
            if not info_item:
                return

            rep = info_item.get('rep')
            if not isinstance(rep, dict):
                return

            licenses = rep.get('assignedLicenses')
            primary_license = licenses[0] if isinstance(licenses, list) and licenses else {}
            if not isinstance(primary_license, dict):
                primary_license = {}

            # Source of truth for user id and tenant is assignedLicenses[0].
            self.user_info = {
                'signavio-user-id': primary_license.get('user', ''),
                'signavio-user-email': rep.get('mail', '') or primary_license.get('mail', ''),
                'signavio-tenant-id': primary_license.get('tenant', ''),
            }
        except Exception:  # noqa: BLE001
            # Ignore parse/network errors and keep waiting for the next matching response.
            pass

    def navigate_and_wait(self, url):
        """
        Navigate to URL and wait for authentication to complete.

        Waits for either:
        1. Detection of authentication cookies (JSESSIONID, token)
        2. Timeout

        Args:
            url: URL to navigate to

        Returns:
            Tuple of (list of cookies, user_info dict)
        """
        self.user_info = {}

        # First check if we already have valid cookies from previous session
        existing_cookies = self.context.cookies()
        has_jsessionid = any(c['name'] == 'JSESSIONID' for c in existing_cookies)
        has_token = any(c['name'] == 'token' for c in existing_cookies)

        if has_jsessionid and has_token:
            print("✓ Found existing valid session. Using saved cookies.")
            return existing_cookies, self.user_info

        # Register response interceptor before navigation to catch /p/user/{id} payload.
        self.page.on('response', self._capture_user_info_from_response)

        # Navigate with timeout in milliseconds
        self.page.goto(url, timeout=self.timeout * 1000)

        # Wait for authentication by checking for cookies
        start_time = time.time()

        cookies_detected_at = None

        while time.time() - start_time < self.timeout:
            cookies = self.context.cookies()
            has_jsessionid = any(c['name'] == 'JSESSIONID' for c in cookies)
            has_token = any(c['name'] == 'token' for c in cookies)

            if has_jsessionid and has_token:
                if self.user_info:
                    # Both cookies and user info are ready.
                    break

                # Give the user-info API a short grace period after cookies appear.
                if cookies_detected_at is None:
                    cookies_detected_at = time.time()
                elif time.time() - cookies_detected_at >= 8:
                    break

            time.sleep(0.5)

        final_cookies = self.context.cookies()
        return final_cookies, self.user_info
        
    def get_cookies(self):
        """Get all cookies from current context."""
        if self.context:
            return self.context.cookies()
        return []
