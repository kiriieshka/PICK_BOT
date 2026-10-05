import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}

DATABASE_URL = os.getenv("DATABASE_URL", "")
DB_ENABLED = os.getenv("DB_ENABLED", "false").lower() in {"1", "true", "yes", "on"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "cards")
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
EXCLUDED_FILE = os.path.join(DATA_DIR, "excluded_players.json")
