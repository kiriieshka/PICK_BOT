import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}

DB_HOST = os.getenv("MYSQL_HOST", os.getenv("DB_HOST", "localhost"))
DB_PORT = int(os.getenv("MYSQL_PORT", os.getenv("DB_PORT", "3306")))
DB_USER = os.getenv("MYSQL_USER", os.getenv("DB_USER", "root"))
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", os.getenv("DB_PASSWORD", ""))
DB_NAME = os.getenv("MYSQL_DATABASE", os.getenv("DB_NAME", "basketball_bot"))
DB_ENABLED = os.getenv("DB_ENABLED", "false").lower() in {"1", "true", "yes", "on"}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARDS_DIR = os.path.join(BASE_DIR, "cards")
DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
EXCLUDED_FILE = os.path.join(DATA_DIR, "excluded_players.json")
