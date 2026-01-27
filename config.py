from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")
OWNER_TG_IDS = [int(i) for i in getenv("OWNER_TG_IDS").split(",")]
ADMIN_CHAT_ID = int(getenv("ADMIN_CHAT_ID"))
ELIXIR_CHAT_ID = int(getenv("ELIXIR_CHAT_ID"))
ELIXIR_THREAD_ID = int(getenv("ELIXIR_THREAD_ID"))

POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_HOST     = getenv("POSTGRES_HOST")
POSTGRES_USER     = getenv("POSTGRES_USER")
POSTGRES_DB       = getenv("POSTGRES_DB")
POSTGRES_PORT     = int(getenv("POSTGRES_PORT"))

SYNC_DB_URL  = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
ASYNC_DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

WORKING_DIR = Path(__file__).parent
PHOTOS_DIR = WORKING_DIR / "photos"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
