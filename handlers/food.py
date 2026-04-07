import json
import os
import random

from handlers.state import get_state, set_state, clear_state

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

with open(os.path.join(DATA_DIR, 'foods.json'), 'r', encoding='utf-8') as f:
    FOODS = json.load(f)

FOOD_TRIGGERS = ['吃什麼', '午餐吃', '晚餐吃', '幫我選', '今天吃', '吃啥', '不知道吃什麼']

FOOD_OPTIONS = ['我要餓死了', '我只想吃一點點', '我想喝東西', '我只是嘴饞']

OPTION_TO_CATEGORY = {
    '我要餓死了': 'starving',
    '我只想吃一點點': 'light',
    '我想喝東西': 'drink',
    '我只是嘴饞': 'snack',
}


def _recommend(category: str) -> str:
    food = random.choice(FOODS[category])
    msg = f"🍽️ 今天就吃「{food['name']}」吧！"
    if food.get('note'):
        msg += f"\n{food['note']}"
    return msg


def handle_food(text: str, user_id: str) -> dict | str | None:
    t = text.strip()

    # 如果正在等待使用者選擇
    if get_state(user_id) == 'FOOD_PICKING':
        if t in OPTION_TO_CATEGORY:
            clear_state(user_id)
            return _recommend(OPTION_TO_CATEGORY[t])
        # 不是有效選項，清掉 state 讓其他 handler 處理
        clear_state(user_id)
        return None

    # 觸發關鍵字 → 問使用者狀態
    if any(kw in t for kw in FOOD_TRIGGERS):
        set_state(user_id, 'FOOD_PICKING')
        return {
            'type': 'quick_reply',
            'text': '你現在有多餓？',
            'options': FOOD_OPTIONS,
        }

    return None
