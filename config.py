from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

OWNER_TG_IDS       = [int(i) for i in getenv("OWNER_TG_IDS").split(",")]
ADMIN_CHAT_ID      = int(getenv("ADMIN_CHAT_ID"))
ELIXIR_CHAT_ID     = int(getenv("ELIXIR_CHAT_ID"))
ELIXIR_THREAD_ID   = int(getenv("ELIXIR_THREAD_ID"))
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")

POSTGRES_DB       = getenv("POSTGRES_DB")
POSTGRES_HOST     = getenv("POSTGRES_HOST")
POSTGRES_USER     = getenv("POSTGRES_USER")
POSTGRES_PORT     = int(getenv("POSTGRES_PORT"))
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")

AMOCRM_CLIENT_ID      = getenv("AMOCRM_CLIENT_ID", "")
AMOCRM_AUTH_CODE      = getenv("AMOCRM_AUTH_CODE", "")
AMOCRM_LONG_TOKEN     = getenv("AMOCRM_LONG_TOKEN", "")
AMOCRM_LOGIN_EMAIL    = getenv("AMOCRM_LOGIN_EMAIL", "")
AMOCRM_BASE_DOMAIN    = getenv("AMOCRM_BASE_DOMAIN", "")
AMOCRM_REDIRECT_URI   = getenv("AMOCRM_REDIRECT_URI", "")
AMOCRM_ACCESS_TOKEN   = getenv("AMOCRM_ACCESS_TOKEN", "")
AMOCRM_CLIENT_SECRET  = getenv("AMOCRM_CLIENT_SECRET", "")
AMOCRM_REFRESH_TOKEN  = getenv("AMOCRM_REFRESH_TOKEN", "")
AMOCRM_LOGIN_PASSWORD = getenv("AMOCRM_LOGIN_PASSWORD", "")

SYNC_DB_URL  = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
ASYNC_DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

WORKING_DIR = Path(__file__).parent
PHOTOS_DIR = WORKING_DIR / "photos"
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
