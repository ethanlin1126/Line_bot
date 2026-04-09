import json
import random
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

with open(os.path.join(DATA_DIR, 'responses.json'), 'r', encoding='utf-8') as f:
    RESPONSES = json.load(f)


TIRED_KEYWORDS = RESPONSES['mood_keywords']['tired']['keywords']
TIRED_RESPONSES = RESPONSES['mood_keywords']['tired']['responses']


def handle_mood(text: str) -> str | None:
    text = text.strip()

    if text.isdigit():
        score = int(text)
        if 1 <= score <= 10:
            pool = RESPONSES['mood_scale'].get(str(score), [])
            if pool:
                return random.choice(pool)

    if any(kw in text for kw in TIRED_KEYWORDS):
        return random.choice(TIRED_RESPONSES)

    return None
