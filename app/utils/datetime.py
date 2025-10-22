from __future__ import annotations

import pytz
from datetime import datetime

UTC_TIME_ZONE = pytz.utc
DEFAULT_TIME_ZONE = "Asia/Tashkent"


def utc_now() -> datetime:
    return datetime.now(UTC_TIME_ZONE)


def convert_datetime_to_timezone(dt: datetime, time_zone: str) -> datetime | None:
    if not dt:
        return None
    if not dt.tzinfo or not time_zone:
        dt = dt.replace(tzinfo=UTC_TIME_ZONE)
    return dt.astimezone(pytz.timezone(zone=time_zone))
