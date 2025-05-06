from datetime import datetime

def get_current_year() -> int:
    """Pure function to get the current year."""
    return datetime.now().year

def get_current_month() -> int:
    """Pure function to get the current month"""
    return datetime.now().month