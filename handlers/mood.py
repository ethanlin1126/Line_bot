import json
import random
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

with open(os.path.join(DATA_DIR, 'responses.json'), 'r', encoding='utf-8') as f:
    RESPONSES = json.load(f)


def handle_mood(text: str) -> str | None:
    text = text.strip()

    # 數字心情評分 1-10
    if text.isdigit():
        score = int(text)
        if 1 <= score <= 10:
            pool = RESPONSES['mood_scale'].get(str(score), [])
            if pool:
                return random.choice(pool)

    # 關鍵字情緒偵測
    for mood, data in RESPONSES['mood_keywords'].items():
        if any(kw in text for kw in data['keywords']):
            return random.choice(data['responses'])

    return None


def checkin_prompt() -> str:
    return (
        "晚安打擾一下 🌙\n\n"
        "今天的你，幾分？\n"
        "（1分很低落 ～ 10分超開心）\n\n"
        "傳個數字給我就好。"
    )
