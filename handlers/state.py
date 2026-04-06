import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite')


def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'CREATE TABLE IF NOT EXISTS user_state '
        '(user_id TEXT PRIMARY KEY, state TEXT)'
    )
    conn.commit()
    return conn


def set_state(user_id: str, state: str):
    with _conn() as conn:
        conn.execute(
            'INSERT OR REPLACE INTO user_state (user_id, state) VALUES (?, ?)',
            (user_id, state)
        )


def get_state(user_id: str) -> str | None:
    with _conn() as conn:
        row = conn.execute(
            'SELECT state FROM user_state WHERE user_id = ?', (user_id,)
        ).fetchone()
    return row[0] if row else None


def clear_state(user_id: str):
    with _conn() as conn:
        conn.execute('DELETE FROM user_state WHERE user_id = ?', (user_id,))
