# Quick start
```
/.dist/sig-cred-cli
```

# building from code
```
./build-sig-cred-cli.sh
/.dist/sig-cred-cli
```

## virtual env
```
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python3 -m playwright install chromium
python3 sig-cred-cli.py
```

# Deactivate virtual env
```
deactivate
```

# Normal run (uses cache if available)
python3 sig-cred-cli.py

# Force fresh login
python3 sig-cred-cli.py --force-refresh

# Which browser
```
python3 sig-cred-cli.py --browser full (google chrome)
python3 sig-cred-cli.py --browser light (google chromium) - Default
```

# With other options
```

python3 sig-cred-cli.py --mask --verbose
python3 sig-cred-cli.py --output json --force-refresh
```


