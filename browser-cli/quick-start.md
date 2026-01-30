# Quick start

./build-cli.sh
/.dist/brow-cli

# building from code
cd browser-cli

## virtual env
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python3 -m playwright install chromium
python3 cli.py


# Deactivate virtual env
deactivate


# Normal run (uses cache if available)
python3 brow-cli.py

# Force fresh login
python3 brow-cli.py --force-refresh

# Which browser
python3 brow-cli.py --browser full (google chrome)
python3 brow-cli.py --browser light (google chromium) - Default

# With other options
python3 brow-cli.py --mask --verbose
python3 brow-cli.py --output json --force-refresh



