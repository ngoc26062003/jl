from datetime import date, timedelta
from zoneinfo import ZoneInfo

PRACTICE_TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")

def award_daily_streak(
    last_practiced_on: date | None,
    current_streak: int,
    total_stars: int,
    today: date,
) -> tuple[int, int, date | None, bool]:
    if last_practiced_on == today:
        return current_streak, total_stars, last_practiced_on, True
    streak = current_streak + 1 if last_practiced_on == today - timedelta(days=1) else 1
    return streak, total_stars + streak, today, False


def active_streak(last_practiced_on: date | None, current_streak: int, today: date) -> int:
    if last_practiced_on is None or last_practiced_on < today - timedelta(days=1):
        return 0
    return current_streak
