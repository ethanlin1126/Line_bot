import json
import random
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

with open(os.path.join(DATA_DIR, 'responses.json'), 'r', encoding='utf-8') as f:
    RESPONSES = json.load(f)


def handle_mood(text: str) -> str | None:
    text = text.strip()

    if text.isdigit():
        score = int(text)
        if 1 <= score <= 10:
            pool = RESPONSES['mood_scale'].get(str(score), [])
            if pool:
                score_reply = random.choice(pool)
                goodnight = random.choice(RESPONSES['night'])
                return f"{score_reply}\n\n{goodnight}"

    return None


def checkin_prompt() -> str:
    return (
        "蔡蓁蓁 晚安🌙\n\n"
        "今天的過得怎麼樣呢？\n"
        "（1分很低落 ～ 10分超開心）\n\n"
        "傳個數字給我～"
    )
