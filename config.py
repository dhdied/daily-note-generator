import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
TEMPLATES_DIR = BASE_DIR / "templates"
LOG_FILE_PATH = LOGS_DIR / "generator.log"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

raw_vault_path = os.getenv("OBSIDIAN_VAULT_PATH", "").strip('"').strip("'")
DAILY_NOTES_FOLDER = os.getenv("DAILY_NOTES_FOLDER", "daily_notes")

if not raw_vault_path:
    raise ValueError("ОШИБКА: Не задан OBSIDIAN_VAULT_PATH в файле .env")

OBSIDIAN_DAILY_DIR = Path(raw_vault_path) / DAILY_NOTES_FOLDER

if not OBSIDIAN_DAILY_DIR.exists():
    print(f"Внимание: Папка {OBSIDIAN_DAILY_DIR} не найдена. Проверьте пути в .env")

WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

CITY_LAT = "55.15402"
CITY_LON = "61.42915"