import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / 'data'
DB_PATH = DATA_DIR / 'app.db'


def load_env_file(path):
    if not path.exists():
        return
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file(PROJECT_DIR / '.env')

WECHAT_APP_ID = os.getenv('WECHAT_APP_ID', '').strip()
WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET', '').strip()
WECHAT_DEFAULT_THUMB_MEDIA_ID = os.getenv('WECHAT_DEFAULT_THUMB_MEDIA_ID', '').strip()
