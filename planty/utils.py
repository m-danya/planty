from datetime import datetime, timezone
import uuid


def get_datetime_now():
    # TODO: think about timezones
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_today():
    return datetime.now(timezone.utc).date()


def generate_uuid():
    return str(uuid.uuid4())
