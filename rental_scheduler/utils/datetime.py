from django.utils import timezone
from typing import Optional

DEFAULT_FMT = '%m/%d/%Y %I:%M %p'


def to_local(dt):
    """Convert an aware datetime to the current TIME_ZONE (local time)."""
    if dt is None:
        return None
    # timezone.localtime will convert from UTC (or any tz) to settings.TIME_ZONE
    return timezone.localtime(dt)


def format_local(dt, fmt: str = DEFAULT_FMT) -> Optional[str]:
    """Return formatted string for datetime in local time or None if dt is None."""
    if dt is None:
        return None
    return timezone.localtime(dt).strftime(fmt)
