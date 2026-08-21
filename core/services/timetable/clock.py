import datetime
from zoneinfo import ZoneInfo
from typing import Optional

KOLKATA_TZ = ZoneInfo("Asia/Kolkata")


def get_current_datetime(now: Optional[datetime.datetime] = None) -> datetime.datetime:
    """
    Returns an aware datetime in Asia/Kolkata timezone.
    
    If 'now' is provided:
    - If naive, assumes or converts to Asia/Kolkata timezone.
    - If aware, converts to Asia/Kolkata timezone.
    If 'now' is None:
    - Returns current system time aware in Asia/Kolkata timezone.
    """
    if now is None:
        return datetime.datetime.now(KOLKATA_TZ)

    if not isinstance(now, datetime.datetime):
        raise TypeError("Expected a datetime.datetime instance for 'now'.")

    if now.tzinfo is None or now.tzinfo.utcoffset(now) is None:
        # Naive datetime provided - localize to Asia/Kolkata
        return now.replace(tzinfo=KOLKATA_TZ)
    else:
        # Aware datetime provided - convert to Asia/Kolkata
        return now.astimezone(KOLKATA_TZ)
