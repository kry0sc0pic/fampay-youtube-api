import datetime


# used to convert datetime.datetime to RFC 3339 format which youtube requires.
def datetime_to_iso(date: datetime.datetime) -> str:
    date = date - datetime.timedelta(microseconds=date.microsecond)
    return date.isoformat() + "Z"
