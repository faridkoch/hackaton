import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "chat_history.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                message_id TEXT NOT NULL,
                step_type TEXT DEFAULT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()


def save_message(chat_id: str, role: str, content: str, message_id: str, step_type: Optional[str] = None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO chat_history (chat_id, role, content, message_id, step_type)
            VALUES (?, ?, ?, ?, ?);
        """, (chat_id, role, content, message_id, step_type))
        conn.commit()


def get_history(chat_id: str) -> List[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT role, content, message_id, step_type, timestamp
            FROM chat_history
            WHERE chat_id = ?
            ORDER BY id ASC;
        """, (chat_id,))
        rows = cursor.fetchall()
    return [
        {
            "type": role,
            "message": content,
            "message_id": message_id,
            "step_type": step_type,

            "timestamp": timestamp,
        }
        for role, content, message_id, step_type, timestamp in rows
    ]
