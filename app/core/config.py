from pathlib import Path

APP_NAME = "Smart File Organizer Pro"
APP_VERSION = "1.0.0"
WINDOW_GEOMETRY = "1200x720"
WINDOW_MIN_SIZE = (900, 600)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "smart_file_organizer.log"
