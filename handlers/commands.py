import os
from datetime import date

from dotenv import load_dotenv

load_dotenv()

UNIT_DATE_STR = os.getenv('UNIT_DATE', '2026-06-05')
DISCHARGE_DATE_STR = os.getenv('DISCHARGE_DATE', '2026-07-24')


def _parse_date(s: str) -> date:
    y, m, d = s.split('-')
    return date(int(y), int(m), int(d))


def _days_until_weekend() -> int:
    today = date.today()
    weekday = today.weekday()
    if weekday >= 5:
        return 0
    return 5 - weekday


def build_countdown_message() -> str:
    today = date.today()
    unit_date = _parse_date(UNIT_DATE_STR)
    discharge_date = _parse_date(DISCHARGE_DATE_STR)
    days_to_unit = (unit_date - today).days
    days_to_discharge = (discharge_date - today).days
    weekend_days = _days_until_weekend()

    if days_to_discharge == 0:
        return "終於退伍了！準備出發澳洲！"

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

    if weekend_days == 0:
        weekend_line = "今天是週末，回家休息了！"
    else:
        weekend_line = f"📅 再 {weekend_days} 天就放假了喔"
    return (
        f"🪖 新訓中\n\n"
        f"距離下部隊還有 {days_to_unit} 天\n"
        f"距離退伍還有 {days_to_discharge} 天 🗓️\n\n"
        f"{weekend_line}"
    )


def handle_command(text: str) -> str | None:
    t = text.strip()

    # --- 倒數 ---
    if any(kw in t for kw in ['還有幾天', '幾天', '倒數', '退伍', '回來', '什麼時候']):
        return build_countdown_message()

    return None
