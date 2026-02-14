# Copilot Instructions

## Project overview
- Python CLI for extracting Signavio authentication cookies via Playwright with an interactive (headed) browser login.
- Extracts exactly two cookies: `JSESSIONID` and `token`; `x-signavio-id` is set to the same value as `token`.
- Main entry point is `browser-cli/brow-cli.py` (caching + Bruno env generation).
- Supporting modules: `browser_controller.py` (Playwright), `extractor.py` (pure parsing), `output.py` (format/mask), `config.py` (defaults).

## Core architecture and boundaries
- Keep extraction logic pure and browser-agnostic in `extractor.py`.
- Keep Playwright browser control isolated in `browser_controller.py`.
- Keep CLI orchestration in `brow-cli.py` using Click.
- Output formatting and masking belong in `output.py`.

## Caching behavior
- Cache location: `.cache/cli/cli-generated.bru` plus `.cache/cli/.cache-timestamp`.
- Cache is valid for 4 hours; `--force-refresh` bypasses cache.
- Cache is parsed from BRU content to rebuild `jsessionid` and `token`.
- When using cache, emit the red/bold warning banner and update Bruno env files.

## Bruno environment file generation
- Search for folders with `API` in the name at project root.
- Create or overwrite `environments/cli-generated.bru` inside each API folder.
- BRU content uses:
  - `signavioId` = token
  - `url` = https://staging.signavio.com
  - `cookie` = `JSESSIONID=<...>; token=<...>;`

## Security and data handling
- Tokens are credentials; avoid logging full tokens unless explicitly requested.
- Honor `--mask` for console output. Do not mask values stored in cache or BRU files.

## CLI usage and behavior
- Default URL: https://staging.signavio.com/p/hub/tasks
- Browser runs in headed mode for SSO login.
- Waits for both cookies (`JSESSIONID` and `token`) or timeout; exit code 1 if missing.
- On Ctrl+C, exit code 130.

## Tests
- Unit tests focus on pure extraction in `browser-cli/tests/test_extractor.py`.
- Run with `pytest -v` or `pytest tests/test_extractor.py -v` from `browser-cli/`.

## When modifying
- Update tests when changing extraction logic or output formatting.
- Keep defaults in `config.py`.
- Prefer small, focused changes and avoid mixing browser code with parsing.
