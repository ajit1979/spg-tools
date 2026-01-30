# Browser Login Cookie Extractor CLI

A Python CLI tool that extracts authentication cookies from browser login sessions using Playwright for Chromium control.

## Features

- **SSO Login Support**: Opens a real browser window for interactive SSO login
- **Cookie Extraction**: Extracts exactly two cookies: `JSESSIONID` and `token`
- **Automatic Header Mapping**: `token` value is also used for `x-signavio-id` header
- **Flexible Output**: Plain text or JSON format
- **Security**: Optional masking of sensitive data
- **Ultra-Simple**: Focused on just two essential cookies

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

### Basic Usage

```bash
python cli.py
```

This will:
1. Open a Chromium browser to https://staging.signavio.com/p/hub/tasks
2. Wait for you to complete the login process
3. Extract `JSESSIONID` and `token` cookies
4. Display tokens (including x-signavio-id which equals token) in plain text format

### Advanced Options

```bash
# Specify custom URL
python cli.py --url https://staging.signavio.com/p/model

# Output as JSON
python cli.py --output json

# Mask sensitive data
python cli.py --mask

# Custom timeout (in seconds)
python cli.py --timeout 600

# Verbose debug output
python cli.py --verbose

# Combine options
python cli.py --url https://staging.signavio.com --output json --mask
```

### CLI Options

- `--url TEXT`: URL to navigate to for login (default: https://staging.signavio.com/p/hub/tasks)
- `--timeout INTEGER`: Timeout in seconds to wait for authentication (default: 300)
- `--output [plain|json]`: Output format (default: plain)
- `--mask`: Mask sensitive data in output
- `--verbose`: Show detailed extraction information for debugging

## How It Works

1. **Browser Launch**: Opens Chromium in headed mode (visible window)
2. **Navigation**: Navigates to the specified URL
3. **User Interaction**: Waits for you to complete SSO login
4. **Token Detection**: Monitors cookies for authentication:
   - JSESSIONID cookie
   - token cookie
   - URL changes
5. **Extraction**: Extracts both cookies and sets x-signavio-id = token
6. **Output**: Formats and displays the extracted tokens

## Security Considerations

⚠️ **Important Security Notes**:

- Extracted tokens provide full access to your account
- Never share unmasked tokens publicly
- Use `--mask` flag when sharing output or in logs
- Store tokens securely (use environment variables or secure vaults)
- Tokens may expire - regenerate as needed
- Be cautious when using `--output json` in scripts that might log output

## Testing

### Run Unit Tests

Unit tests cover the pure extraction logic without browser interaction:

```bash
pytest tests/test_extractor.py -v
```

### Run All Tests

```bash
pytest -v
```

### Run Integration Tests (Optional)

Integration tests require browser automation and are marked as slow:

```bash
pytest -v -m integration
```

## Examples

### Example Output (Plain Text)

```
Opening browser to: https://staging.signavio.com/p/hub/tasks
Please complete the login process. Waiting up to 300 seconds...

============================================================
Extracted Tokens:
============================================================
JSESSIONID: A1B2C3D4E5F6G7H8I9J0
TOKEN: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SIGNAVIO_ID: user-12345
```

### Example Output (JSON)

```json
{
  "jsessionid": "195917C00ABC008DE3D2385BFF6368AA",
  "token": "6926521bd90b446ba607f87b642d4302",
  "x-signavio-id": "6926521bd90b446ba607f87b642d4302"
}
```

**Note:** `token` and `x-signavio-id` always have the same value.

### Example Output (Masked)

```
JSESSIONID: A1B2**************J0
TOKEN: eyJh**************************VCJ9
SIGNAVIO_ID: user**********345
```

## Troubleshooting

### No tokens extracted

- Ensure you completed the login process
- Check if the login was successful (you reached the authenticated page)
- Try with `--verbose` to see what cookies were found
- Increase timeout with `--timeout`

### Browser doesn't open

- Ensure Playwright Chromium is installed: `playwright install chromium`
- Check for conflicting browser processes

### Playwright not found

- Install requirements: `pip install -r requirements.txt`
- Verify installation: `python -c "import playwright; print(playwright.__version__)"`

## Development

### Project Structure

```
browser-cli/
├── cli.py                  # Main CLI entry point
├── browser_controller.py   # Playwright browser control
├── extractor.py           # Pure extraction logic
├── output.py              # Outpucookie t formatting
├── config.py              # Configuration constants
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── tests/
    └── test_extractor.py # Unit tests for extraction logic
```

### Adding New Features

1. Keep extraction logic in `extractor.py` (pure functions, no browser code)
2. Add browser interactions to `browser_controller.py`
3. Update CLI options in `cli.py`
4. Write unit tests in `tests/test_extractor.py`

## License

MIT
