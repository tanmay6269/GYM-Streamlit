from datetime import datetime


def valid_id(value):
    """Return the id as an int, or None if it isn't a whole positive number."""
    value = str(value).strip()
    return int(value) if value.isdigit() else None


def valid_date(value):
    """Return a YYYY-MM-DD string, or None if it isn't a real date."""
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return None


def valid_mobile(value):
    value = str(value).strip()
    return value if value.isdigit() and 7 <= len(value) <= 15 else None
