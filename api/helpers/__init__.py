import datetime


def datetime_to_iso(date: datetime.datetime) -> str:
    date = date - datetime.timedelta(microseconds=date.microsecond)
    return date.isoformat() + "Z"
