# Browser-CLI Functional Specifications

## Executive Summary

The **Browser-CLI** is a Python-based command-line tool that automates the extraction of authentication tokens from browser login sessions. It leverages Playwright for browser automation to handle SSO (Single Sign-On) flows and extracts authentication credentials (JSESSIONID and token cookies) from the Signavio platform.

The tool is designed to streamline API testing workflows by eliminating the need to manually extract authentication cookies from browser sessions, with intelligent caching to avoid redundant logins within 4-hour intervals.

---

## 1. Core Purpose & Problem Statement

### Problem
- Manual extraction of authentication cookies from browser sessions is time-consuming and error-prone
- SSO login flows require interactive user authentication that cannot be automated
- API testing tools (Bruno, Postman, cURL) need fresh authentication credentials
- Repeated logins waste time and server resources

### Solution
- Automate cookie extraction from interactive browser login sessions
- Provide intelligent caching to reuse valid credentials
- Generate ready-to-use environment configuration files for API testing tools
- Support multiple output formats and security options

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       brow-cli.py (Main Entry Point)            │
│                      - Click CLI Framework                       │
│                      - User interaction & orchestration          │
└─────────────────────────────────────────────────────────────────┘
                                  │
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
        ┌─────────────────┐ ┌──────────────┐ ┌─────────────┐
        │ Cache Manager   │ │ Browser      │ │ Token       │
        │ (4-hr validity) │ │ Controller   │ │ Extractor   │
        │ Functions:      │ │ (Playwright) │ │ (Pure Logic)│
        │ - check_cache() │ │              │ │             │
        │ - save_cache()  │ │ Functions:   │ │ Functions:  │
        │ - validate_age()│ │ - navigate() │ │ - extract() │
        └─────────────────┘ │ - wait()     │ └─────────────┘
                            │ - get_cookies()     │
                            └──────────────┘      │
                                                  │
                            ┌─────────────────────┘
                            ▼
                    ┌──────────────────────┐
                    │ Output Formatter     │
                    │ & Security Handler   │
                    │                      │
                    │ Functions:           │
                    │ - format_output()    │
                    │ - mask_data()        │
                    └──────────────────────┘
                                  │
                                  ▼
                    ┌──────────────────────────┐
                    │ Bruno Environment Files  │
                    │ Generator                │
                    │                          │
                    │ - Find API folders       │
                    │ - Create environments/   │
                    │ - Write cli-generated.bru│
                    └──────────────────────────┘
```

---

## 3. Component Specifications

### 3.1 Main CLI Module: `brow-cli.py`

**Purpose**: Orchestrate the entire authentication flow with caching support

**Command-Line Options**:

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--url` | TEXT | https://staging.signavio.com/p/hub/tasks | URL to navigate for login |
| `--timeout` | INTEGER | 300 | Wait timeout in seconds (5 minutes) |
| `--output` | CHOICE | plain | Output format: `plain` or `json` |
| `--mask` | FLAG | False | Mask sensitive data in output |
| `--verbose` | FLAG | False | Show debug information |
| `--browser` | CHOICE | light | Browser type: `light` (Chromium) or `full` (Chrome) |
| `--force-refresh` | FLAG | False | Ignore cache, perform fresh login |

**Exported Tokens**:
```python
{
    'jsessionid': 'string',      # JSESSIONID cookie value
    'token': 'string',            # token cookie value
    'x-signavio-id': 'string'     # Same as token (for headers)
}
```

**Key Functions**:

| Function | Purpose | Returns |
|----------|---------|---------|
| `main()` | CLI entry point, orchestrates entire flow | None (exits with code) |
| `find_api_folders()` | Locates folders containing "API" in name | List[Path] |
| `generate_bruno_env_files()` | Creates cli-generated.bru in API folders | None |
| `get_cache_dir()` | Returns cache directory path | Path |
| `get_cache_files()` | Returns cache file paths tuple | Tuple[Path, Path] |
| `is_cache_valid()` | Validates cache age (< 4 hours) | bool |
| `save_to_cache()` | Persists tokens and timestamp | None |
| `check_cache()` | Loads cache if valid | Dict or None |

---

### 3.2 Browser Controller: `browser_controller.py`

**Purpose**: Manage Playwright browser automation for SSO login flows

**Key Class**: `BrowserController`

**Context Manager Pattern**: Automatic resource cleanup via `__enter__` and `__exit__`

**Key Methods**:

| Method | Purpose | Returns |
|--------|---------|---------|
| `__init__()` | Initialize controller with settings | None |
| `__enter__()` | Start browser session | self |
| `__exit__()` | Clean up browser resources | None |
| `navigate_and_wait()` | Navigate to URL, wait for auth cookies | List[Dict] |
| `get_cookies()` | Retrieve all cookies from context | List[Dict] |
| `_ensure_browsers_installed()` | Auto-install Playwright browsers | None |
| `_set_browser_path_env()` | Configure browser cache path | None |

**Platform Support**:
- **macOS**: Browsers cached to `~/Library/Caches/ms-playwright`
- **Linux**: Browsers cached to `~/.cache/ms-playwright`

**Authentication Detection**: Waits for both JSESSIONID and token cookies to appear

---

### 3.3 Token Extractor: `extractor.py`

**Purpose**: Pure extraction logic (no browser dependencies, unit-testable)

**Key Functions**:

| Function | Input | Output | Logic |
|----------|-------|--------|-------|
| `extract_from_cookies()` | List[Dict] cookies | Dict tokens | Scans cookies for JSESSIONID and token, copies token to x-signavio-id |
| `parse_cookies()` | String cookie_string | List[Dict] | Parses "name1=val1; name2=val2" format |

---

### 3.4 Output Formatter: `output.py`

**Purpose**: Format tokens for display and apply security masking

**Key Functions**:

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `format_output()` | Format tokens for display | Dict, format_type | String |
| `mask_sensitive_data()` | Mask token values | Dict tokens | Dict masked |

**Masking Algorithm**:
- Shows first 4 characters
- Shows last 4 characters
- Replaces middle with asterisks
- Example: `abc123def456ghi` → `abc1**....**ghi`

---

### 3.5 Configuration: `config.py`

**Purpose**: Centralized configuration constants

```python
DEFAULT_URL = "https://staging.signavio.com/p/hub/tasks"
DEFAULT_TIMEOUT = 300  # seconds (5 minutes)
DEFAULT_OUTPUT = "plain"
```

---

## 4. Execution Flow

### 4.1 Complete Flow (First Run / Force Refresh)

```
START (user runs brow-cli.py [options])
    │
    ├─► Parse CLI arguments
    │
    ├─► Check --force-refresh flag
    │   │
    │   ├─ If NOT set → Check cache validity
    │   │   │
    │   │   ├─ Cache valid & < 4 hours
    │   │   │  │
    │   │   │  ├─► Load cached tokens
    │   │   │  ├─► Display RED warning: "USING CACHED DATA"
    │   │   │  ├─► Format output (apply --mask if set)
    │   │   │  ├─► Generate Bruno files from cache
    │   │   │  └─► EXIT (success)
    │   │   │
    │   │   └─ Cache invalid/expired/missing
    │   │      (continue to fresh login)
    │   │
    │   └─ If SET (--force-refresh)
    │      (continue to fresh login)
    │
    ├─► FRESH LOGIN FLOW:
    │   │
    │   ├─► Initialize BrowserController
    │   │
    │   ├─► Enter context manager (__enter__)
    │   │   ├─ Ensure browsers installed
    │   │   ├─ Set environment paths
    │   │   ├─ Start Playwright session
    │   │   ├─ Launch browser
    │   │   └─ Create context & page
    │   │
    │   ├─► Navigate to login URL
    │   │
    │   ├─► WAIT FOR AUTHENTICATION
    │   │   ├─ Poll cookies every 0.5 seconds
    │   │   ├─ Check for JSESSIONID cookie
    │   │   ├─ Check for token cookie
    │   │   ├─ Wait max --timeout seconds
    │   │   └─ Return cookies when both found
    │   │
    │   ├─► Extract tokens from cookies
    │   │   ├─ Search JSESSIONID
    │   │   ├─ Search token
    │   │   └─ Set x-signavio-id = token
    │   │
    │   ├─► Apply masking (if --mask flag)
    │   │
    │   ├─► Format output (--output format)
    │   │
    │   ├─► Display extracted tokens
    │   │
    │   ├─► Validate extraction success
    │   │   ├─ If failed → print error & EXIT(1)
    │   │   └─ If success → continue
    │   │
    │   ├─► Find API folders (containing "API" in name)
    │   │
    │   ├─► Generate Bruno env files
    │   │   ├─ For each API folder:
    │   │   │   ├─ Create environments/ directory
    │   │   │   ├─ Write cli-generated.bru with tokens
    │   │   │   └─ Print ✓ confirmation
    │   │   └─ End loop
    │   │
    │   ├─► Save to cache
    │   │   ├─ Create .cache/cli/ directory
    │   │   ├─ Write cli-generated.bru (formatted)
    │   │   ├─ Write .cache-timestamp (ISO 8601)
    │   │   └─ Mark as cached
    │   │
    │   ├─► Exit context manager (__exit__)
    │   │   ├─ Close page
    │   │   ├─ Close context
    │   │   ├─ Close browser
    │   │   └─ Stop Playwright
    │   │
    │   └─► EXIT(0) SUCCESS
    │
    └─► ERROR HANDLING
        ├─ KeyboardInterrupt → print "cancelled" & EXIT(130)
        ├─ Exception → print error & EXIT(1)
        └─ Validation errors → print warning & EXIT(1)
```

---

## 5. Caching System

### 5.1 Cache Structure

```
.cache/
└── cli/
    ├── cli-generated.bru      # Token data in BRU format
    └── .cache-timestamp       # Creation timestamp (ISO 8601)
```

### 5.2 Cache Validation Logic

**Validity Check**:
1. Both files exist
2. Parse timestamp: `datetime.fromisoformat(timestamp_str)`
3. Calculate age: `now - cache_time`
4. Valid if: `age < timedelta(hours=4)`

**Invalid Conditions**:
- Either file missing
- Timestamp format invalid
- Timestamp unparseable
- Age ≥ 4 hours

### 5.3 Cache Parsing

**Input Format** (cli-generated.bru):
```
vars {
  signavioId: 3c91836c35d446939dcab40519dcabde
  url: https://staging.signavio.com
  cookie: JSESSIONID=595559A29079ABA6107BB64D2A4D945F; token=3c91836c35d446939dcab40519dcabde;
}
```

**Extraction Logic**:
- Extract `signavioId` → token & x-signavio-id
- Extract `JSESSIONID` from cookie line

---

## 6. Bruno Environment File Generation

### 6.1 Target Structure

```
Asset APIs/
├── environments/
│   ├── cli-generated.bru      (auto-generated)
│   ├── stage.bru              (manual)
│   └── ...
├── *.bru files                (API requests)
└── bruno.json

Attribute APIs/
├── environments/
│   ├── cli-generated.bru      (auto-generated)
│   └── ...
└── ...
```

### 6.2 Generated File Content

```bru
vars {
  signavioId: {extracted_token}
  url: https://staging.signavio.com
  cookie: JSESSIONID={jsessionid}; token={token};
}
```

---

## 7. Security Features

### 7.1 Data Masking

When `--mask` flag is used:
- Tokens are masked for display
- Format: `XXXX****...****YYYY` (first 4 + last 4 chars visible)
- Stored unmask in cache and Bruno files (for actual use)

### 7.2 Sensitive Data Handling

- Cache files stored in user's project directory (local)
- No tokens logged to console (unless --verbose + active extraction)
- Bruno files contain actual tokens (needed for API calls)
- Environment isolation via context managers

---

## 8. Error Handling & Exit Codes

| Exit Code | Scenario |
|-----------|----------|
| 0 | Success |
| 1 | General error (token extraction failed, token validation failed, API folder not found) |
| 130 | User cancelled (Ctrl+C) |

**Error Conditions**:
- Missing JSESSIONID or token cookies
- Timeout waiting for authentication
- Browser initialization failure
- API folder not found
- File system errors (cache write, Bruno file write)

---

## 9. Dependencies & Requirements

### 9.1 python3 Packages
```
click>=8.0.0          # CLI framework
playwright>=1.40.0    # Browser automation
```

### 9.2 System Requirements
- python3 3.7+
- Playwright browsers (auto-installed via `playwright install chromium`)
- 500MB+ disk space (for browser binaries)

### 9.3 Browser Support
- **Chromium** (light): 100% supported
- **Chrome** (full): Supported if installed on system

---

## 10. Use Cases

### 10.1 First-Time Setup
```bash
python3 brow-cli.py
# Credentials extracted, cached, Bruno files generated
```

### 10.2 Repeated Usage (Same Session)
```bash
python3 brow-cli.py  # Uses cache if < 4 hours
# No browser opens, credentials displayed from cache
```

### 10.3 Force Fresh Login
```bash
python3 brow-cli.py --force-refresh
# Ignores cache, opens browser, new login required
```

### 10.4 Secure Output for Sharing
```bash
python3 brow-cli.py --mask --output json
# Returns masked tokens in JSON format
```

### 10.5 Integration with CI/CD
```bash
python3 brow-cli.py --output json > tokens.json
# Use tokens.json in subsequent API testing steps
```

---

## 11. Future Enhancement Possibilities

- [ ] Multi-user cache (encrypted per-user)
- [ ] Automatic token refresh before 4-hour expiry
- [ ] Headless mode with pre-stored credentials
- [ ] Integration with system keychain
- [ ] Token expiry monitoring
- [ ] Multiple environment support (.env generation)
- [ ] Webhook callback for token updates

---

## 12. Testing Strategy

### 12.1 Unit Tests (Pure Functions)
- `test_extractor.py`: Tests `extract_from_cookies()` without browser
- No Playwright dependency for unit tests
- Fast, isolated, repeatable

### 12.2 Integration Tests (Future)
- End-to-end flows
- Cache validation
- Bruno file generation

### 12.3 Manual Testing
- Real login flows
- Cross-platform browser behavior
- Timeout edge cases

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-30 | Initial comprehensive specifications with caching, Mermaid diagram |

