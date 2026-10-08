from pathlib import Path

APP_NAME = "TGBackupTool"
APP_VERSION = "2.0.0"

APP_DATA_DIR = Path.home() / ".tg_backup_tool"
APP_DATA_DIR.mkdir(exist_ok=True)

SESSIONS_DIR = APP_DATA_DIR / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

SETTINGS_FILE = APP_DATA_DIR / "settings.json"
LOG_FILE = APP_DATA_DIR / "app.log"

DONATE_URL = "https://boosty.to/igorshelloffdev"
GITHUB_URL = "https://github.com/Igor-Shelloff"
TELEGRAM_URL = "https://t.me/igor_shelloff"

DEFAULT_SETTINGS = {
    "api_id": "",
    "api_hash": "",
    "phone": "",
    "session_name": "backup_session",
    "language": "en",
    "appearance": "Dark",
    "silent_log": True,
}