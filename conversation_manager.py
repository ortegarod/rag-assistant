import logging
from typing import List, Dict
import sqlite3
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, db_path: str = 'conversations.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    role TEXT,
                    content TEXT
                )
            ''')
            # Ensure session_id column exists for per-visitor chats
            try:
                cursor.execute("PRAGMA table_info(conversations)")
                cols = [row[1] for row in cursor.fetchall()]
                if 'session_id' not in cols:
                    cursor.execute("ALTER TABLE conversations ADD COLUMN session_id TEXT DEFAULT 'default'")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session_ts ON conversations(session_id, timestamp)")
            except Exception:
                # Best-effort; continue even if migration fails
                pass
            conn.commit()

    def add_message(self, role: str, content: str, session_id: str = 'default'):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO conversations (role, content, session_id) VALUES (?, ?, ?)',
                (role, content, session_id)
            )
            conn.commit()

    def get_recent_messages(self, limit: int = 20, session_id: str = 'default') -> List[Dict[str, str]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT role, content FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?',
                (session_id, limit)
            )
            return [{'role': role, 'content': content} for role, content in cursor.fetchall()][::-1]

    def clear_history(self, session_id: str | None = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if session_id:
                cursor.execute('DELETE FROM conversations WHERE session_id = ?', (session_id,))
            else:
                cursor.execute('DELETE FROM conversations')
            conn.commit()

    def summarize_old_conversations(self, days_old: int = 7):
        # This method would summarize conversations older than 'days_old'
        # and replace them with a summary in the database
        # Implementation depends on the specific summarization logic you want to use
        pass

    def prune_old_conversations(self, days_old: int = 30):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM conversations WHERE timestamp < datetime("now", ?)',
                (f'-{days_old} days',)
            )
            conn.commit()
