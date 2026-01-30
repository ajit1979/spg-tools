# Caching Implementation Guide

## Overview
The browser CLI now implements intelligent caching to avoid redundant browser logins.

## How It Works

### Cache Structure
```
.cache/cli/
├── cli-generated.bru        # Cached credential file
└── .cache-timestamp         # ISO format timestamp of cache creation
```

### Cache Behavior

1. **First Run**: Browser opens normally, credentials extracted, and cached
2. **Subsequent Runs (< 4 hours)**: 
   - Returns cached credentials instantly
   - Displays red warning message
   - Updates Bruno env files from cache
   - No browser interaction needed
3. **Force Refresh**: Use `--force-refresh` flag to bypass cache

## Usage Examples

### Normal run (uses cache if available)
```bash
python brow-cli.py
```

### Force fresh login (bypasses cache)
```bash
python brow-cli.py --force-refresh
```

### With other options
```bash
python brow-cli.py --output json --force-refresh
python brow-cli.py --mask --verbose
```

## Cache Behavior Details

- **Cache Location**: `.cache/cli/` directory in current working directory
- **Cache Duration**: 4 hours from creation time
- **Timestamp Format**: ISO 8601 (datetime.isoformat())
- **Invalid Cache**: Auto-deleted by creating new valid cache
- **Parsing**: BRU format file automatically parsed to extract tokens

## Message Output

When using cache, you'll see:
```
============================================================
USING CACHED DATA
(Data from last login - less than 4 hours old)
To refresh, run with --force-refresh
============================================================
```

This message is displayed in **RED** and **BOLD** to clearly indicate cached data is being used.

## Implementation Details

### New Functions

1. **`get_cache_dir()`** - Returns `.cache/cli` path
2. **`get_cache_files()`** - Returns tuple of cache file paths
3. **`is_cache_valid()`** - Checks if cache exists and is < 4 hours old
4. **`save_to_cache(tokens)`** - Saves tokens and timestamp
5. **`check_cache()`** - Loads and validates cache, returns tokens or None

### Modified Functions

1. **`main()`** - Added `--force-refresh` flag and cache check logic
2. **`generate_bruno_env_files()`** - Unchanged, works with both fresh and cached tokens

## Benefits

✅ Faster repeated execution (skips browser login)
✅ Reduces server load from repeated authentication
✅ Automatic timestamp validation
✅ Easy manual refresh with `--force-refresh`
✅ Clear visual feedback when using cached data
