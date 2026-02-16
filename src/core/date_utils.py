"""
Date parsing utilities for flexible date format support
"""

from datetime import datetime
from typing import Tuple


def parse_flexible_date(date_str: str) -> Tuple[datetime, str]:
    """
    Parse date in multiple formats and return both datetime and ISO-normalized string.

    Supported input formats:
    - YYYY-M-D  (e.g., 2027-7-14)
    - YYYY-MM-DD (e.g., 2027-07-14)
    - DD/MM/YYYY (e.g., 14/07/2027)
    - D/M/YYYY  (e.g., 14/7/2027)

    Returns:
        tuple: (datetime object, ISO string YYYY-MM-DD for internal use)
    """
    formats = [
        '%Y-%m-%d',  # 2027-07-14 or 2027-7-14
        '%d/%m/%Y',  # 14/07/2027 or 14/7/2027
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            normalized = dt.strftime('%Y-%m-%d')  # ISO 8601: 2027-07-14
            return dt, normalized
        except ValueError:
            continue

    raise ValueError(
        f"Invalid date format: '{date_str}'. "
        f"Supported formats: YYYY-M-D, YYYY-MM-DD, DD/MM/YYYY, D/M/YYYY"
    )
