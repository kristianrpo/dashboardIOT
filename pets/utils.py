from datetime import datetime
def format_date(date):
    """
    Formats a date string to a more readable format.

    Args:
        date (str): The date string to format.

    Returns:
        str: The formatted date string.
    """
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ") if date else None
