#!/bin/bash
set -e

echo "Installing Playwright browsers..."
#playwright install chromium chrome

echo "Building standalone CLI executable..."
pyinstaller --onefile \
  --collect-all playwright \
  --hidden-import=playwright \
  --hidden-import=playwright._impl \
  --hidden-import=subprocess \
  --runtime-tmpdir=/tmp \
  browser-cli/sig-cred-cli.py

echo "✓ Build complete! Executable: ./dist/sig-cred-cli"
