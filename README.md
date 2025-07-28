
This Python script is an advanced keylogger designed for educational purposes and authorized red-team simulations. Here's a breakdown of its key components:
Core Features:

Keylogging Capabilities:
Captures all keyboard input (alphanumeric keys and special keys)
Differentiates between character keys and special keys (Enter, Shift, Ctrl, etc.)
Logs with precise timestamps

Red-Team Features:
Persistence Mechanisms:
Windows: Registry autorun
Linux: Cron job
macOS: Launchd service

Encryption:
AES-128 encryption using Fernet
Key management system

Email Reporting (Simulated):
Scheduled log delivery
Configurable intervals

Operational Modes:
Educational mode (default)
Red-team mode (with advanced features)

Security Features:
Graceful termination with ESC key
Encrypted log storage
Ethical usage warnings

Technical Specifications:
Dependencies: pynput, cryptography

Output Files:
keystrokes.log: Plaintext log of keystrokes
keystrokes.enc: Encrypted version of logs
keylogger_config.key: Encryption key


Step-by-Step Execution Guide

Prerequisites:
Install Python (3.6+ recommended)
Install required packages:
pip install pynput cryptography
Running the Keylogger:

1. Educational Mode (Default):
python keylogger.py --educational
Basic keylogging only
Logs to console and keystrokes.log
Press ESC to exit

3. Red-Team Simulation Mode:
python keylogger.py --red-team --email your@email.com --password your_password
Enables all advanced features
Installs persistence mechanism
Encrypts logs
Simulates email reporting
Press ESC to exit

5. Command Options:
--educational    # Run in basic educational mode
--red-team       # Enable advanced red-team features
--email          # Set email for reports (red-team only)
--password       # Email password (red-team only)
--interval       # Email interval in seconds (default: 600)

6. Cleanup:
# Remove all generated files:
del keystrokes.log keystrokes.enc keylogger_config.key

