from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo

def now_in_tz(tz_name: str):
    tz = ZoneInfo(tz_name or "UTC")
    return datetime.now(tz)

def today_in_tz(tz_name: str):
    return now_in_tz(tz_name).date()
