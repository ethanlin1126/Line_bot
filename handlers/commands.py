import json
import random
import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

with open(os.path.join(DATA_DIR, 'responses.json'), 'r', encoding='utf-8') as f:
    RESPONSES = json.load(f)

with open(os.path.join(DATA_DIR, 'songs.json'), 'r', encoding='utf-8') as f:
    SONGS = json.load(f)

with open(os.path.join(DATA_DIR, 'therapy.json'), 'r', encoding='utf-8') as f:
    THERAPY = json.load(f)

UNIT_DATE_STR = os.getenv('UNIT_DATE', '2026-06-05')
DISCHARGE_DATE_STR = os.getenv('DISCHARGE_DATE', '2026-07-24')


def _parse_date(s: str) -> date:
    y, m, d = s.split('-')
    return date(int(y), int(m), int(d))


def _days_until_weekend() -> int:
    """返回距離下一個週六或週日的天數（今天是週末則為 0）"""
    today = date.today()
    weekday = today.weekday()  # 0=Mon … 5=Sat, 6=Sun
    if weekday >= 5:
        return 0
    return 5 - weekday  # 距離週六幾天


SONG_STATE_FILE = os.path.join(DATA_DIR, 'song_state.json')


def _load_used_songs() -> list:
    if os.path.exists(SONG_STATE_FILE):
        with open(SONG_STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def _save_used_songs(used: list) -> None:
    with open(SONG_STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(used, f, ensure_ascii=False)


def handle_command(text: str) -> str | None:
    t = text.strip()

    # --- 音樂 ---
    if any(kw in t for kw in ['音樂', '推薦歌', '聽什麼歌', '給我一首歌', '給我一首']):
        used = _load_used_songs()
        remaining = [s for s in SONGS if s['title'] not in used]
        if not remaining:
            _save_used_songs([])
            return "歌單裡的歌都推薦過了！重新洗牌，下次再問我吧 🔁"
        song = random.choice(remaining)
        used.append(song['title'])
        _save_used_songs(used)
        msg = f"🎵 {song['title']} — {song['artist']}"
        if song.get('note'):
            msg += f"\n\n{song['note']}"
        if song.get('spotify'):
            msg += f"\n\n▶️ {song['spotify']}"
        return msg

    
    # --- 倒數 ---
    if any(kw in t for kw in ['還有幾天', '幾天', '倒數', '退伍', '回來', '什麼時候']):
        today = date.today()
        unit_date = _parse_date(UNIT_DATE_STR)
        discharge_date = _parse_date(DISCHARGE_DATE_STR)
        days_to_unit = (unit_date - today).days
        days_to_discharge = (discharge_date - today).days
        weekend_days = _days_until_weekend()

        # 退伍當天
        if days_to_discharge == 0:
            return "終於退伍了！準備出發澳洲！"

        # 下部隊後（服役中）
        if days_to_unit <= 0:
            if weekend_days == 0:
                weekend_line = "今天是週末，回家休息了！"
            else:
                weekend_line = f"📅 再 {weekend_days} 天就週末了"
            return (
                f"🪖 下部隊中\n\n"
                f"距離退伍還有 {days_to_discharge} 天 🗓️\n"
                f"{weekend_line}"
            )

        # 新訓中
        if weekend_days == 0:
            weekend_line = "今天是週末，回家休息了！"
        else:
            weekend_line = f"📅 下次放假再 {weekend_days} 天"
        return (
            f"🪖 新訓中\n\n"
            f"距離下部隊還有 {days_to_unit} 天\n"
            f"距離退伍還有 {days_to_discharge} 天 🗓️\n\n"
            f"{weekend_line}"
        )

    
    # --- 如果你在 ---
    if any(kw in t for kw in ['如果你在', '如果我在', '你在的話']):
        return random.choice(RESPONSES['if_i_were_there'])

    # --- 今天不用努力 ---
    if any(kw in t for kw in ['今天不用努力', '不用努力', '可以廢']):
        return random.choice(RESPONSES['no_need_to_try'])

    # --- 療癒提案 ---
    if any(kw in t for kw in ['今天要幹嘛', '無聊', '給我一個提案', '療癒']):
        return random.choice(THERAPY['proposals'])

    # --- 休息一下 ---
    if any(kw in t for kw in ['累了', '休息一下', '好累', '想休息']):
        return random.choice(THERAPY['rest'])

    return None
