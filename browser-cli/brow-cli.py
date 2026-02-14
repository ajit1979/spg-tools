#!/usr/bin/env python3
"""
CLI for extracting authentication tokens from browser login sessions.
"""

import click
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from browser_controller import BrowserController
from extractor import extract_from_cookies
from output import format_output, mask_sensitive_data
from config import DEFAULT_URL, DEFAULT_TIMEOUT


@click.command()
@click.option(
    '--url',
    default=DEFAULT_URL,
    help='URL to navigate to for login. Default: https://staging.signavio.com/p/hub/tasks'
)
@click.option(
    '--timeout',
    default=DEFAULT_TIMEOUT,
    type=int,
    help='Timeout in seconds to wait for authentication. Default: 300'
)
@click.option(
    '--output',
    default='plain',
    type=click.Choice(['plain', 'json'], case_sensitive=False),
    help='Output format: plain or json. Default: plain'
)
@click.option(
    '--mask',
    is_flag=True,
    help='Mask sensitive data in output for security'
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Show detailed extraction information for debugging'
)
@click.option(
    '--browser',
    default='light',
    type=click.Choice(['light', 'full'], case_sensitive=False),
    help='Browser type: light (Chromium) or full (Chrome). Default: light'
)
@click.option(
    '--force-refresh',
    is_flag=True,
    help='Ignore cache and perform fresh browser login'
)
def main(url, timeout, output, mask, verbose, browser, force_refresh):
    """
    Extract authentication tokens from browser login session.
    
    This tool opens a Chromium browser, waits for you to complete the SSO login,
    then extracts authentication tokens (cookies, headers) for API access.
    
    Use --force-refresh to bypass cache and perform fresh login.
    Cache is valid for 4 hours.
    """
    # Check cache before opening browser
    if not force_refresh:
        cached_result = check_cache()
        if cached_result:
            click.echo("\n" + "="*60)
            click.secho("USING CACHED DATA", fg='red', bold=True)
            click.secho("(Data from last login - less than 4 hours old)", fg='red')
            click.secho("To refresh, run with --force-refresh", fg='red', bold=True)
            click.echo("="*60)
            
            # Keep unmasked result for file operations
            display_result = cached_result.copy()
            
            # Display cached tokens
            click.echo("\n" + "="*60)
            click.echo("Cached Tokens:")
            click.echo("="*60)
            if mask:
                display_result = mask_sensitive_data(display_result)
            output_str = format_output(display_result, output_format=output)
            click.echo(output_str)
            
            # Generate/update Bruno files and VS Code settings from cache
            click.echo("\n" + "="*60)
            click.echo("Updating Bruno environment files from cache...")
            click.echo("="*60)
            generate_bruno_env_files(cached_result)
            update_vscode_settings_file(cached_result)
            return
    
    click.echo(f"Opening browser to: {url}")
    click.echo(f"Please complete the login process. Waiting up to {timeout} seconds...")
    
    try:
        controller = BrowserController(headless=False, timeout=timeout, browser_type=browser)
        
        with controller:
            # Navigate to URL and wait for cookies
            cookies = controller.navigate_and_wait(url)
            
            if verbose:
                click.echo(f"\nDebug: Found {len(cookies)} cookies")
                for c in cookies:
                    click.echo(f"  - {c['name']}: {c['value'][:30]}..." if len(c['value']) > 30 else f"  - {c['name']}: {c['value']}")
            
            # Extract tokens from cookies
            result = extract_from_cookies(cookies)
            
            if verbose:
                click.echo(f"Debug: Extracted tokens: {result}")
            
            # Keep unmasked result for file operations
            unmasked_result = result.copy()
            
            # Apply masking if requested
            if mask:
                result = mask_sensitive_data(result)
            
            # Format output
            output_str = format_output(result, output_format=output)
            click.echo("\n" + "="*60)
            click.echo("Extracted Tokens:")
            click.echo("="*60)
            click.echo(output_str)
            
            if not result or all(v is None for v in result.values()):
                click.echo("\nWarning: No tokens were extracted. Login may have failed.", err=True)
                sys.exit(1)
            
            # Generate Bruno environment files and update VS Code settings with unmasked tokens
            click.echo("\n" + "="*60)
            click.echo("Generating Bruno environment files...")
            click.echo("="*60)
            generate_bruno_env_files(unmasked_result)
            update_vscode_settings_file(unmasked_result)
            
            # Save to cache
            save_to_cache(unmasked_result)
                
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(130)
    except Exception as e:
        click.echo(f"\nError: {e}", err=True)
        sys.exit(1)


def find_api_folders(base_path=None):
    """
    Find all folders with 'API' in their name.
    
    Args:
        base_path: Root path to search from. Defaults to current directory.
        
    Returns:
        List of Path objects for folders containing 'API'
    """
    if base_path is None:
        base_path = Path.cwd()
    else:
        base_path = Path(base_path)
    
    api_folders = []
    for item in base_path.iterdir():
        if item.is_dir() and 'API' in item.name:
            api_folders.append(item)
    
    return api_folders


def generate_bruno_env_files(tokens):
    """
    Generate cli-generated.bru files in environments folders under API directories.
    
    Args:
        tokens: Dict with keys 'jsessionid', 'token', 'x-signavio-id'
    """
    # Extract values
    signavio_id = tokens.get('token') or tokens.get('x-signavio-id')
    jsessionid = tokens.get('jsessionid')
    token = tokens.get('token')
    
    if not signavio_id or not jsessionid:
        click.echo("Warning: Could not extract required tokens (JSESSIONID and token)", err=True)
        return
    
    # Find API folders
    api_folders = find_api_folders()
    
    if not api_folders:
        click.echo("No folders with 'API' in name found in current directory.")
        return
    
    for api_folder in api_folders:
        # Create environments folder if it doesn't exist
        env_folder = api_folder / 'environments'
        env_folder.mkdir(exist_ok=True)
        
        # Create or overwrite cli-generated.bru file
        bru_file = env_folder / 'cli-generated.bru'
        
        # Create content
        content = f"""vars {{
  signavioId: {signavio_id}
  url: https://staging.signavio.com
  cookie: JSESSIONID={jsessionid}; token={token};
}}
"""
        
        # Write file
        bru_file.write_text(content)
        click.echo(f"✓ Created {bru_file.relative_to(Path.cwd())}")


def update_vscode_settings_file(tokens):
    """
    Update .vscode/settings.json with authentication tokens.
    
    Args:
        tokens: Dict with keys 'jsessionid', 'token', 'x-signavio-id'
    """
    # Extract values
    signavio_id = tokens.get('token') or tokens.get('x-signavio-id')
    jsessionid = tokens.get('jsessionid')
    token = tokens.get('token')
    
    if not signavio_id or not jsessionid:
        click.echo("Warning: Could not extract required tokens for settings file", err=True)
        return
    
    settings_path = Path.cwd() / '.vscode' / 'settings.json'
    
    # Create .vscode directory if it doesn't exist
    settings_path.parent.mkdir(exist_ok=True)
    
    # Read existing settings or create new dict
    if settings_path.exists():
        try:
            settings = json.load(open(settings_path, 'r'))
        except (json.JSONDecodeError, IOError):
            settings = {}
    else:
        settings = {}
    
    # Ensure structure exists
    if 'java.test.config' not in settings:
        settings['java.test.config'] = {}
    if 'env' not in settings['java.test.config']:
        settings['java.test.config']['env'] = {}
    
    # Update environment variables
    settings['java.test.config']['env']['X_SIGNAVIO_ID'] = signavio_id
    settings['java.test.config']['env']['SIGNAVIO_COOKIE'] = f"JSESSIONID={jsessionid}; token={token};"
    
    # Write back to file
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=4)
    
    click.echo(f"✓ Updated {settings_path.relative_to(Path.cwd())}")


def get_cache_dir():
    """
    Get the cache directory in the current working directory.
    
    Returns:
        Path object for .cache/cli directory
    """
    cache_dir = Path.cwd() / '.cache' / 'cli'
    return cache_dir


def get_cache_files():
    """
    Get paths to cache files.
    
    Returns:
        Tuple of (cache_data_file, cache_timestamp_file)
    """
    cache_dir = get_cache_dir()
    cache_data = cache_dir / 'cli-generated.bru'
    cache_timestamp = cache_dir / '.cache-timestamp'
    return cache_data, cache_timestamp


def is_cache_valid():
    """
    Check if cache exists and is less than 4 hours old.
    
    Returns:
        Boolean indicating if cache is valid
    """
    cache_data, cache_timestamp = get_cache_files()
    
    # Check if both files exist
    if not cache_data.exists() or not cache_timestamp.exists():
        return False
    
    try:
        # Read timestamp
        timestamp_str = cache_timestamp.read_text().strip()
        cache_time = datetime.fromisoformat(timestamp_str)
        
        # Check if less than 4 hours old
        now = datetime.now()
        age = now - cache_time
        max_age = timedelta(hours=4)
        
        return age < max_age
    except (ValueError, IOError):
        return False


def save_to_cache(tokens):
    """
    Save tokens and timestamp to cache.
    
    Args:
        tokens: Dict with keys 'jsessionid', 'token', 'x-signavio-id'
    """
    cache_dir = get_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    cache_data, cache_timestamp = get_cache_files()
    
    # Create bru content
    signavio_id = tokens.get('token') or tokens.get('x-signavio-id')
    jsessionid = tokens.get('jsessionid')
    token = tokens.get('token')
    
    content = f"""vars {{
  signavioId: {signavio_id}
  url: https://staging.signavio.com
  cookie: JSESSIONID={jsessionid}; token={token};
}}
"""
    
    # Save cache data
    cache_data.write_text(content)
    
    # Save timestamp
    timestamp = datetime.now().isoformat()
    cache_timestamp.write_text(timestamp)


def check_cache():
    """
    Check if valid cache exists and load it.
    
    Returns:
        Dict with cached tokens if valid cache exists, None otherwise
    """
    if not is_cache_valid():
        return None
    
    cache_data, cache_timestamp = get_cache_files()
    
    try:
        # Parse the cached bru file to extract tokens
        content = cache_data.read_text()
        
        # Simple parsing of bru format
        result = {
            'jsessionid': None,
            'token': None,
            'x-signavio-id': None
        }
        
        # Extract signavioId
        if 'signavioId:' in content:
            sig_id = content.split('signavioId:')[1].split('\n')[0].strip()
            result['token'] = sig_id
            result['x-signavio-id'] = sig_id
        
        # Extract JSESSIONID and token from cookie line
        if 'cookie:' in content:
            cookie_line = content.split('cookie:')[1].split(';')[0].strip()
            if 'JSESSIONID=' in cookie_line:
                jsessionid = cookie_line.split('JSESSIONID=')[1].strip()
                result['jsessionid'] = jsessionid
        
        return result if result['jsessionid'] and result['token'] else None
    except (IOError, IndexError):
        return None



if __name__ == '__main__':
    main()
