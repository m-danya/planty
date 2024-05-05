from datetime import datetime, timezone


def get_datetime_now():
    return datetime.now(timezone.utc)


def get_today():
    return datetime.now(timezone.utc).date()
