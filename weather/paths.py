"""weather アプリのファイル配置。すべて __file__ 基準なので作業ディレクトリに依存しない。"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PLACES_JSON = DATA_DIR / "places.json"
SETTINGS_JSON = BASE_DIR / "settings.json"
CACHE_JSON = BASE_DIR / "cache.json"
ICON_CACHE_DIR = BASE_DIR / "icon_cache"
EXPORT_HTML = BASE_DIR / "weather_forecast.html"

BASE_URL = "https://tenki.jp"
MAX_DAYS = 14
