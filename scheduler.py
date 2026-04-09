import os
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
RENDER_URL = os.getenv('RENDER_URL', '')
USER_ID = os.getenv('USER_ID')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

with open(os.path.join(DATA_DIR, 'schedule.json'), 'r', encoding='utf-8') as f:
    SCHEDULE = json.load(f)



# ── 推送函式 ──────────────────────────────────────────────

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
        print('[scheduler] USER_ID not set, skipping memory push')
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


# ── 訊息發送邏輯 ──────────────────────────────────────────


def _send_countdown():
    from handlers.commands import build_countdown_message
    push_message(build_countdown_message())



def keep_alive():
    if RENDER_URL:
        try:
            requests.get(f'{RENDER_URL}/ping', timeout=10)
            print('[keep_alive] pinged')
        except Exception as e:
            print(f'[keep_alive] error: {e}')


# ── 排程分派 ──────────────────────────────────────────────

def _make_job(job_config: dict):
    """根據 schedule.json 的設定回傳對應的 job 函式。"""

    # 直接指定文字
    if 'text' in job_config:
        text = job_config['text']
        return lambda t=text: push_message(t)

    job_type = job_config.get('type', '')

    if job_type == 'memory':
        if 'image_id' in job_config:
            image_url = f"https://lh3.googleusercontent.com/d/{job_config['image_id']}"
            text = job_config.get('text', '')
            return lambda u=image_url, t=text: push_memory_message(u, t)
        print(f'[scheduler] memory 缺少 image_id：{job_config}')
        return None

    if job_type == 'countdown':
        return _send_countdown

    print(f'[scheduler] 未知的 job 設定：{job_config}')
    return None


# ── 啟動排程 ──────────────────────────────────────────────

def start_scheduler() -> BackgroundScheduler:
    from datetime import datetime
    scheduler = BackgroundScheduler(timezone='Australia/Sydney')

    for date_str, date_data in SCHEDULE['dates'].items():
        date = datetime.strptime(date_str, '%Y-%m-%d')

        for job_config in date_data['schedule']:
            hour, minute = map(int, job_config['time'].split(':'))
            fn = _make_job(job_config)
            if fn is None:
                continue
            scheduler.add_job(
                fn,
                'cron',
                year=date.year,
                month=date.month,
                day=date.day,
                hour=hour,
                minute=minute,
            )


    # 每 10 分鐘 ping 自己，防止 Render 休眠
    scheduler.add_job(keep_alive, 'interval', minutes=10)

    scheduler.start()
    print('[scheduler] 排程已啟動')
    return scheduler
