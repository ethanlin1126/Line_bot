import os
import random
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
RENDER_URL = os.getenv('RENDER_URL', '')
USER_ID = os.getenv('USER_ID')
DISCHARGE_DATE_STR = os.getenv('DISCHARGE_DATE', '2026-07-24')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

with open(os.path.join(DATA_DIR, 'responses.json'), 'r', encoding='utf-8') as f:
    RESPONSES = json.load(f)

with open(os.path.join(DATA_DIR, 'quotes.json'), 'r', encoding='utf-8') as f:
    QUOTES = json.load(f)

with open(os.path.join(DATA_DIR, 'songs.json'), 'r', encoding='utf-8') as f:
    SONGS = json.load(f)

with open(os.path.join(DATA_DIR, 'therapy.json'), 'r', encoding='utf-8') as f:
    THERAPY = json.load(f)

with open(os.path.join(DATA_DIR, 'memories.json'), 'r', encoding='utf-8') as f:
    MEMORIES = json.load(f)


def push_message(text: str):
    if not USER_ID or USER_ID == 'your_line_user_id_here':
        print(f'[scheduler] USER_ID not set, skipping push: {text[:30]}')
        return
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
    }
    payload = {
        'to': USER_ID,
        'messages': [{'type': 'text', 'text': text}],
    }
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        print(f'[push_message] error: {resp.status_code} {resp.text}')


def push_memory_message(image_url: str, text: str):
    if not USER_ID or USER_ID == 'your_line_user_id_here':
        print(f'[scheduler] USER_ID not set, skipping memory push')
        return
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
    }
    payload = {
        'to': USER_ID,
        'messages': [
            {
                'type': 'image',
                'originalContentUrl': image_url,
                'previewImageUrl': image_url,
            },
            {'type': 'text', 'text': text},
        ],
    }
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        print(f'[push_memory_message] error: {resp.status_code} {resp.text}')

# 早上
def send_morning():
    quote = random.choice(QUOTES['daily'])
    msg = random.choice(RESPONSES['morning'])
    push_message(f"{msg}\n\n{quote}")

LAST_NOON_FILE = os.path.join(DATA_DIR, '.last_noon')


def _get_last_noon() -> str:
    try:
        with open(LAST_NOON_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ''


def _save_last_noon(choice: str):
    with open(LAST_NOON_FILE, 'w') as f:
        f.write(choice)


# 中午
def send_noon_therapy():
    options = ['song', 'text', 'proposal']
    last = _get_last_noon()
    if last in options:
        options.remove(last)
    choice = random.choice(options)
    _save_last_noon(choice)
    if choice == 'song':
        s = random.choice(SONGS)
        text = f"午安 🎵\n\n今天推薦你一首歌：\n{s['title']} — {s['artist']}"
        if s.get('note'):
            text += f"\n\n{s['note']}"
        if s.get('spotify'):
            text += f"\n\n▶️ {s['spotify']}"
        push_message(text)
    elif choice == 'text':
        push_message(f"午安 ☀️\n\n{random.choice(THERAPY['texts'])}")
    else:
        push_message(f"午安 🌿\n\n今天的小提案：\n{random.choice(THERAPY['proposals'])}")


def send_checkin():
    from handlers.mood import checkin_prompt
    push_message(checkin_prompt())


def send_random_no_effort():
    push_message(random.choice(RESPONSES['no_need_to_try']))


def send_discharge_countdown():
    from handlers.commands import build_countdown_message
    push_message(build_countdown_message())


MEMORY_STATE_FILE = os.path.join(DATA_DIR, '.last_memory')


def _get_last_memory() -> str:
    try:
        with open(MEMORY_STATE_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return ''


def _save_last_memory(image_id: str):
    with open(MEMORY_STATE_FILE, 'w') as f:
        f.write(image_id)


def send_memory():
    last = _get_last_memory()
    remaining = [m for m in MEMORIES if m['image_id'] != last]
    if not remaining:
        remaining = MEMORIES
    memory = random.choice(remaining)
    _save_last_memory(memory['image_id'])
    image_url = f"https://lh3.googleusercontent.com/d/{memory['image_id']}"
    push_memory_message(image_url, memory['text'])


def keep_alive():
    if RENDER_URL:
        try:
            requests.get(f'{RENDER_URL}/ping', timeout=10)
            print('[keep_alive] pinged')
        except Exception as e:
            print(f'[keep_alive] error: {e}')

# 排程訊息
def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone='Asia/Taipei')

    # 每日
    scheduler.add_job(send_morning, 'cron', hour=10, minute=0)
    scheduler.add_job(send_noon_therapy, 'cron', hour=16, minute=0)
    scheduler.add_job(send_checkin, 'cron', hour=0, minute=0)

    # 每週一、四：倒數提醒
    scheduler.add_job(send_discharge_countdown, 'cron', day_of_week='mon,thu', hour=20, minute=0)

    # 每週三：今天不用努力
    scheduler.add_job(send_random_no_effort, 'cron', day_of_week='wed', hour=19, minute=0)

    # 每週二、五：傳送回憶照片
    scheduler.add_job(send_memory, 'cron', day_of_week='tue,fri', hour=22, minute=0)

    # 每 10 分鐘 ping 自己，防止 Render 休眠
    scheduler.add_job(keep_alive, 'interval', minutes=10)

    scheduler.start()
    print('[scheduler] 排程已啟動')
    return scheduler
