import sqlite3
import os
import re
from datetime import datetime, timezone, timedelta

from handlers.state import get_state, set_state, clear_state

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'db.sqlite')
TZ_TAIPEI = timezone(timedelta(hours=8))

DIARY_TRIGGER = re.compile(r'^日記[：:：]?\s*(.+)', re.DOTALL)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        'CREATE TABLE IF NOT EXISTS diary '
        '(id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)'
    )
    conn.commit()
    return conn


def save_diary(content: str) -> str:
    now = datetime.now(TZ_TAIPEI).strftime('%Y-%m-%d %H:%M')
    with _conn() as conn:
        conn.execute('INSERT INTO diary (content, created_at) VALUES (?, ?)', (content, now))
    return f"記下來了📝\n\n「{content[:30]}{'...' if len(content) > 30 else ''}」\n\n我假日會好好看完的~"


def handle_diary(text: str, user_id: str) -> str | None:
    t = text.strip()

    # 正在等使用者輸入日記內容
    if get_state(user_id) == 'DIARY_MODE':
        clear_state(user_id)
        return save_diary(t)

    # Rich menu 觸發
    if t == '我想跟你說...':
        set_state(user_id, 'DIARY_MODE')
        return "發生什麼事了呢？跟我說我在聽\n（把想說的話傳給我，我會幫你記下來）"

    # 格式：日記：內容
    m = DIARY_TRIGGER.match(t)
    if m:
        return save_diary(m.group(1).strip())

    # 查看最近日記
    if t in ['我的日記', '日記紀錄', '看日記']:
        with _conn() as conn:
            rows = conn.execute(
                'SELECT content, created_at FROM diary ORDER BY id DESC LIMIT 5'
            ).fetchall()
        if not rows:
            return "還沒有日記。\n按「我想跟你說...」開始記錄 🌙"
        lines = ['最近的日記 🌙\n']
        for content, created_at in rows:
            time_str = created_at[:16].replace('T', ' ') if created_at else ''
            lines.append(f"[{time_str}]\n{content}\n")
        return '\n'.join(lines)

    return None
