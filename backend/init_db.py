import json
import sqlite3

from .config import DB_PATH, DATA_DIR


def init_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT DEFAULT '',
            body TEXT NOT NULL,
            cover_image TEXT DEFAULT '',
            content_type TEXT DEFAULT 'article',
            tags TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            summary TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
            cover_image TEXT DEFAULT '',
            extra_config TEXT DEFAULT '{}',
            validation_warnings TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS publish_tasks (
            id TEXT PRIMARY KEY,
            content_id INTEGER,
            platform_draft_id INTEGER,
            platform TEXT NOT NULL,
            account_id INTEGER,
            mode TEXT DEFAULT 'simulate',
            status TEXT DEFAULT 'pending',
            title TEXT DEFAULT '',
            error_message TEXT DEFAULT '',
            publish_url TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            finished_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
