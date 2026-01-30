"""
Browser controller using Playwright to manage Chromium sessions.
"""

from playwright.sync_api import sync_playwright
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
                
    def navigate_and_wait(self, url):
        """
        Navigate to URL and wait for authentication to complete.
        
        Waits for either:
        1. Detection of authentication cookies (JSESSIONID, token)
        2. Timeout
        
        Args:
            url: URL to navigate to
            
        Returns:
            List of cookies
        """
        # First check if we already have valid cookies from previous session
        existing_cookies = self.context.cookies()
        has_jsessionid = any(c['name'] == 'JSESSIONID' for c in existing_cookies)
        has_token = any(c['name'] == 'token' for c in existing_cookies)
        
        if has_jsessionid and has_token:
            print("✓ Found existing valid session. Using saved cookies.")
            return existing_cookies
        
        # Navigate with timeout in milliseconds
        self.page.goto(url, timeout=self.timeout * 1000)
        
        # Store initial URL to track changes
        initial_url = self.page.url
        
        # Wait for authentication by checking for cookies
        start_time = time.time()
        authenticated = False
        
        while time.time() - start_time < self.timeout:
            # Check cookies
            cookies = self.context.cookies()
            
            # Look for authentication indicators
            has_jsessionid = any(c['name'] == 'JSESSIONID' for c in cookies)
            has_token = any(c['name'] == 'token' for c in cookies)
            
            if has_jsessionid and has_token:
                authenticated = True
                # Give a bit more time for all cookies to be set
                time.sleep(2)
                break
                
            time.sleep(0.5)
        
        # Get final cookies
        final_cookies = self.context.cookies()
        
        return final_cookies
        
    def get_cookies(self):
        """Get all cookies from current context."""
        if self.context:
            return self.context.cookies()
        return []
