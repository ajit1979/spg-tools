# Browser-CLI Tool - Instructions for AI Coding Agents

path: ./browser-cli

## Overview

This is a Python-based CLI tool that extracts authentication tokens from browser login sessions using Playwright for browser automation. The tool is specifically designed for SSO/OAuth login flows where users must interact with a browser to authenticate.

## Purpose

**Problem Solved:** Extract authentication cookies after completing browser-based SSO login flows.

**Primary Use Case:** Get JSESSIONID and token cookies from Signavio applications after SSO authentication for use in API testing tools (Bruno, Postman, cURL). The tool also provides x-signavio-id (which is set to the same value as token).

## Architecture & Design Principles

### Core Design Pattern: Separation of Concerns

1. **Pure Functions (extractor.py)**: All parsing/extraction logic is browser-agnostic and easily testable
2. **Browser Automation (browser_controller.py)**: Playwright-specific code isolated here
3. **CLI Interface (cli.py)**: User interaction and orchestration only
4. **Utilities (output.py, config.py)**: Supporting functions with single responsibilities

### Key Architectural Decisions

- **Headed Browser Mode**: Required for SSO login - user must interact with the browser
- **Cookie-Only Extraction**: Simplified to extract only JSESSIONID and token cookies
- **Token Duplication**: x-signavio-id is set to the same value as token
- **Timeout-Based Detection**: Polls for authentication indicators rather than waiting for specific events

## File Structure & Responsibilities

```
browser-cli/
├── cli.py                   # CLI entry point - Click framework, orchestration
├── browser_controller.py    # Playwright browser control, network interception
├── extractor.py            # Pure extraction logic (NO browser dependencies)
├── output.py               # Formatting (plain/JSON) and masking utilities
├── config.py               # Configuration constants (URLs, timeouts, defaults)
├── requirements.txt        # Python dependencies
├── README.md              # User-facing documentation
├── instructions.md        # This file - AI agent documentation
└── tests/
    └── test_extractor.py  # Unit tests for pure extraction functions
```

## Component Details

### 1. cli.py - CLI Entry Point

**Responsibilities:**
- Parse command-line arguments using Click
- Orchestrate the authentication flow
- Handle errors and user interrupts
- Format and display output

**Key Functions:**
- `main()`: CLI entry point with Click decorators

**Options:**
- `--url`: Target URL for login (default: https://staging.signavio.com/p/hub/tasks)
- `--timeout`: Wait time in seconds (default: 300)
- `--output`: Format (plain/json)
- `--mask`: Enable sensitive data masking

**Control Flow:**
1. Initialize BrowserController
2. Navigate to URL and wait for authentication
3. Extract cookies (JSESSIONID and token only)
4. Apply masking if requested
5. Format and display output

### 2. browser_controller.py - Browser Automation

**Responsibilities:**
- Launch and manage Playwright Chromium browser
- Navigate to URLs and wait for authentication
- Extract cookies from browser context

**Key Class: BrowserController**

**Methods:**
- `__init__(headless=False, timeout=300)`: Initialize with settings
- `__enter__()` / `__exit__()`: Context manager for resource cleanup
- `navigate_and_wait(url)`: Navigate and poll for authentication completion
- `get_cookies()`: Retrieve all cookies from browser context

**Authentication Detection Logic:**
Polls for these indicators:
1. JSESSIONID cookie present
2. token cookie present

**Important:** Browser runs in headed mode (headless=False) to allow user interaction with SSO login forms.

### 3. extractor.py - Pure Extraction Logic

**Responsibilities:**
- Parse cookies to extract authentication tokens (JSESSIONID and token only)
- Duplicate token value to x-signavio-id field
- NO browser dependencies - pure functions only
- Fully unit-testable without Playwright

**Key Functions:**

#### `extract_from_cookies(cookies)`
- **Input:** List of cookie dicts `[{'name': str, 'value': str}, ...]`
- **Returns:** `{jsessionid: str|None, token: str|None, 'x-signavio-id': str|None}`
- **Logic:** 
  - Extracts JSESSIONID cookie value → jsessionid field
  - Extracts token cookie value → token field
  - Sets x-signavio-id to same value as token (duplicated)
- **Example:**
  ```python
  # Input cookies: JSESSIONID=ABC123; token=XYZ789
  # Output: {'jsessionid': 'ABC123', 'token': 'XYZ789', 'x-signavio-id': 'XYZ789'}
  ```

### 4. output.py - Output Formatting

**Responsibilities:**
- Format extracted tokens for display
- Mask sensitive data

**Key Functions:**

#### `format_output(data, output_format='plain')`
- **Input:** Token dict, format ('plain' or 'json')
- **Returns:** Formatted string
- **Plain format:** `KEY: value` per line
- **JSON format:** Pretty-printed JSON

#### `mask_sensitive_data(data, mask_char='*', show_chars=4)`
- **Input:** Token dict
- **Returns:** Dict with masked values
- **Logic:** Shows first 4 and last 4 chars, masks middle with asterisks
- **Example:** `A1B2C3D4E5F6G7H8` → `A1B2**********G7H8`

### 5. config.py - Configuration

**Responsibilities:**
- Centralize default values
- Make defaults easy to modify

**Constants:**
- `DEFAULT_URL = "https://staging.signavio.com/p/hub/tasks"`
- `DEFAULT_TIMEOUT = 300`
- `DEFAULT_METHOD = "auto"`
- `DEFAULT_OUTPUT = "plain"`

## Testing Strategy

### Unit Tests (tests/test_extractor.py)

**Coverage:**
- All extraction functions in extractor.py
- Edge cases: empty inputs, None values, malformed data
- Integration scenarios: multiple extraction methods

**Run Tests:**
```bash
pytest tests/test_extractor.py -v
```

**Test Classes:**
- `TestExtractFromCookies`: Cookie extraction scenarios (JSESSIONID and token only)
- Edge cases: empty cookies, missing cookies, partial cookies

**Why No Browser Tests:**
- Browser tests are slow and fragile
- Pure functions are tested without Playwright dependencies
- Manual testing required for full browser integration

## Common Modification Scenarios

### Scenario 1: Add Support for New Cookie

**Files to Modify:**
1. [extractor.py](extractor.py) - Add new cookie to return dict in extract_from_cookies()
2. [tests/test_extractor.py](tests/test_extractor.py) - Add test cases for new cookie
3. [browser_controller.py](browser_controller.py) - Add detection logic if needed

**Example:**
```python
# In extractor.py, update return dict:
result = {
    'jsessionid': None,
    'token': None,
    'x-signavio-id': None,
    'new_cookie_name': None  # Add this
}

# Add extraction logic in loop:
for cookie in cookies:
    if cookie['name'] == 'JSESSIONID':
        result['jsessionid'] = cookie['value']
    elif cookie['name'] == 'token':
        result['token'] = cookie['value']
        result['x-signavio-id'] = cookie['value']
    elif cookie['name'] == 'NewCookieName':  # Add this
        result['new_cookie_name'] = cookie['value']
```

### Scenario 2: Change Default URL or Timeout

**Files to Modify:**
1. [config.py](config.py) - Update constant values

**Example:**
```python
# In config.py
DEFAULT_URL = "https://production.signavio.com/p/hub"
DEFAULT_TIMEOUT = 600  # 10 minutes
```

### Scenario 3: Add New CLI Option

**Files to Modify:**
1. [cli.py](cli.py) - Add Click option decorator and parameter
2. Update logic in main() function to use new parameter

**Example:**
```python
@click.option(
    '--verbose',
    is_flag=True,
    help='Enable verbose output'
)
def main(url, timeout, method, output, mask, verbose):
    if verbose:
        click.echo(f"Debug: Starting with URL {url}")
```

### Scenario 4: Change Output Format

**Files to Modify:**
1. [output.py](output.py) - Add new format in `format_output()`
2. [cli.py](cli.py) - Add to output choices

**Example:**
```python
# In output.py
def format_output(data, output_format='plain'):
    if output_format == 'json':
        return json.dumps(data, indent=2)
    elif output_format == 'yaml':
        return yaml.dump(data)
    else:
        # plain format
        ...
```

## Dependencies

### Required Packages (requirements.txt)

- **playwright>=1.40.0**: Browser automation
- **click>=8.1.0**: CLI framework
- **pytest>=7.4.0**: Testing framework
- **pytest-playwright>=0.4.0**: Playwright test integration

### Installation Steps

```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers (CRITICAL - often forgotten)
playwright install chromium
```

## Execution Flow

### Normal Execution Path

1. User runs: `python cli.py [options]`
2. Click parses arguments → `main()` function
3. `BrowserController` initialized (headless=False, timeout from args)
4. Context manager `__enter__()` starts Playwright and launches browser
5. `navigate_and_wait(url)` called:
   - Browser navigates to URL
   - Polling loop checks for JSESSIONID and token cookies every 0.5s
   - Breaks when both cookies detected or timeout reached
6. `extract_from_cookies()` extracts JSESSIONID and token, duplicates token to x-signavio-id
7. `mask_sensitive_data()` applied if --mask flag set
8. `format_output()` formats for display
9. Output printed to console
10. Context manager `__exit__()` closes browser and cleans up

### Error Handling

- **KeyboardInterrupt**: User Ctrl+C → exit code 130
- **Timeout**: No tokens after timeout → warning message, exit code 1
- **Browser Launch Failure**: Playwright errors → error message, exit code 1
- **No Tokens Extracted**: Warning message but completes gracefully

## Key Patterns & Conventions

### 1. Context Manager Pattern
```python
with BrowserController() as controller:
    # Resources auto-cleaned on exit
```

### 2. Pure Functions in extractor.py
- No side effects
- No global state
- Always return same output for same input
- Easy to test

### 3. Default Parameters
- All functions have sensible defaults
- Optional parameters clearly documented
- Defaults defined in config.py for consistency

### 4. Dict Return Values
```python
# Standard return format for extract_from_cookies():
{
    'jsessionid': str | None,
    'token': str | None,
    'x-signavio-id': str | None  # Always same value as token
}
```

### 5. Error Messages to stderr
```python
click.echo("Error message", err=True)
```

## Important Implementation Details

### Why Polling Instead of Events?

The authentication flow doesn't have a reliable "done" event. We poll for:
- Presence of specific cookies
- Specific headers in responses
- URL changes

This is more robust than waiting for page load or network idle.

### Why Headed Browser?

SSO login requires user interaction:
- Username/password input
- MFA/2FA codes
- OAuth consent screens

Headless mode cannot handle these interactive elements.

### Why Token Duplication?

In Signavio's authentication model, the token cookie value is also used as the x-signavio-id header in API requests. By extracting both and setting them to the same value, the tool provides all necessary authentication data in one extraction.

### Thread Safety

Not thread-safe. Browser automation is inherently single-threaded. Do not attempt to:
- Run multiple BrowserController instances in parallel
- Share browser context between threads

## Security Considerations

### Sensitive Data Handling

1. **Tokens are credentials**: Full account access
2. **Masking**: Use --mask flag to partially hide tokens
3. **Output redirection**: Be careful with `> file.txt` - tokens exposed
4. **Environment variables**: Prefer storing in env vars over files

### Best Practices for AI Agents

When modifying this tool:
- Never log full tokens in debug output
- Default to masked output in shared environments
- Document security implications of new features
- Add warnings for insecure operations

## Troubleshooting Guide

### Issue: "playwright not found"
**Solution:** Run `playwright install chromium`

### Issue: No tokens extracted
**Possible causes:**
1. Login not completed - user didn't finish SSO flow
2. Timeout too short - increase with --timeout
3. Cookies disabled in browser profile
4. Wrong cookie names - verify JSESSIONID and token cookies exist

**Debugging:**
1. Add print statements in polling loop to see what cookies are present
2. Increase timeout and manually inspect browser state
3. Check browser DevTools → Application → Cookies to verify cookie names

### Issue: Browser doesn't open
**Possible causes:**
1. Playwright browsers not installed
2. Display/X11 issues on Linux
3. Permission issues

**Solution:** 
- Reinstall: `playwright install chromium --force`
- Check Playwright install location: `playwright install --help`

### Issue: Tests fail
**Common causes:**
1. Missing pytest: `pip install pytest`
2. Changed function signatures without updating tests
3. Test assertions too strict

## Future Enhancement Ideas

### Potential Features to Add

1. **Headless mode with pre-auth**: If cookies provided, skip browser
2. **Multiple URL support**: Try fallback URLs if first fails
3. **Cookie export**: Save to Netscape cookie format
4. **Browser profile support**: Use existing Chrome profile
5. **Screenshot on failure**: Debug what went wrong
6. **Proxy support**: Route through corporate proxy
7. **Multiple browser support**: Firefox, WebKit options
8. **Watch mode**: Keep browser open, re-extract periodically
9. **Token validation**: Test if extracted tokens work
10. **Credential vault**: Store/retrieve from keychain

### Code Quality Improvements

1. Add type hints throughout (Python 3.10+)
2. Add docstrings to all functions
3. Increase test coverage to 100%
4. Add integration tests with mocked Playwright
5. Add logging with configurable verbosity
6. Add configuration file support (.env or YAML)
7. Add CI/CD pipeline (GitHub Actions)

## Working with This Tool as an AI Agent

### When User Asks to Modify

1. **Read relevant files first**: Don't assume - check current implementation
2. **Maintain separation of concerns**: Keep pure functions pure
3. **Update tests**: Every code change should have test changes
4. **Update docs**: README.md and this file
5. **Test command examples**: Update start-app-read-me.md if CLI changes

### When User Reports a Bug

1. **Check test coverage**: Does test exist for this scenario?
2. **Add failing test first**: Reproduce bug in test
3. **Fix code**: Make test pass
4. **Add regression test**: Prevent future occurrence

### When Adding New Features

1. **Start with extractor.py**: Add pure function first
2. **Add tests**: Verify pure function works
3. **Add browser integration**: Update browser_controller.py if needed
4. **Add CLI option**: Update cli.py last
5. **Document**: Update all relevant docs

## Quick Reference Commands

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run with defaults
python cli.py

# Run tests
pytest tests/test_extractor.py -v

# Get JSON output
python cli.py --output json

# Extended timeout
python cli.py --timeout 600

# Custom URL
python cli.py --url https://example.com/login

# Masked output
python cli.py --mask

# Verbose output
python cli.py --verbose

# Help
python cli.py --help
```

## Summary for AI Agents

**This tool is:**
- A CLI for extracting authentication cookies (JSESSIONID and token) from browser SSO logins
- Ultra-simplified: cookie-only extraction, no headers, no URL parsing
- Special behavior: token value is duplicated to x-signavio-id field
- Architected with separation of concerns (pure functions + browser automation)
- Well-tested (comprehensive test coverage for two-cookie extraction)
- Extensible (clear modification points for adding new cookies)

**When working with this code:**
- Maintain the pure function pattern in extractor.py
- Update tests with every code change
- Keep browser automation isolated in browser_controller.py
- Document changes in user-facing and AI-facing docs
- Consider security implications of modifications
- Remember: token and x-signavio-id always have the same value

**Key files for most changes:**
- Adding cookie extraction → [extractor.py](extractor.py) + tests
- Changing browser behavior → [browser_controller.py](browser_controller.py)
- Adding CLI options → [cli.py](cli.py)
- Changing defaults → [config.py](config.py)

**Current extraction model:**
- Input: Browser cookies after SSO login
- Output: `{jsessionid, token, x-signavio-id}` where x-signavio-id = token value
- Only JSESSIONID and token cookies are extracted, everything else is ignored
