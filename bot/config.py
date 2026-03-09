"""Configuration module for Grad Service bot."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FILES_DIR = DATA_DIR / "files"
DATABASE_PATH = DATA_DIR / "grad_service.db"

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = tuple(
    int(admin_id.strip())
    for admin_id in ADMIN_IDS_RAW.split(",")
    if admin_id.strip()
)
YANDEX_GEOCODER_API_KEY = os.getenv("YANDEX_GEOCODER_API_KEY", "")

HOUR_SECONDS = 3600
DEADLINE_MIN_HOURS = 23
DEADLINE_MAX_HOURS = 25
