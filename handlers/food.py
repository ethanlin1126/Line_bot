import json
import os
import random

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

with open(os.path.join(DATA_DIR, 'foods.json'), 'r', encoding='utf-8') as f:
    FOODS = json.load(f)

FOOD_TRIGGERS = ['吃什麼', '午餐吃', '晚餐吃', '幫我選', '今天吃', '吃啥', '不知道吃什麼']


def handle_food(text: str) -> str | None:
    t = text.strip()
    if not any(kw in t for kw in FOOD_TRIGGERS):
        return None
    food = random.choice(FOODS)
    msg = f"🍽️ 今天就吃「{food['name']}」吧！"
    if food.get('note'):
        msg += f"\n{food['note']}"
    return msg
