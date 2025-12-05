"""
Utility functions for FabManager Data Analyzer

This module provides helper functions for data cleaning, sanitization,
and formatting.
"""

import re
from typing import Any


def sanitize_filename(name: str) -> str:
    """
    Return a safe filename string.

    Removes or replaces characters that are not safe for filenames.

    Args:
        name: Original filename or string

    Returns:
        Sanitized string safe for use in filenames

    Example:
        >>> sanitize_filename("My File: Name/With*Bad?Chars")
        'My_File__Name_With_Bad_Chars'
    """
    sanitized = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
    return sanitized or "unknown"


def clean_data_for_json(data: Any) -> Any:
    """
    Recursively clean data to remove unusual line terminators.

    Replaces Unicode line separators (LS - U+2028) and paragraph separators (PS - U+2029)
    with standard newlines to avoid JSON compatibility issues.

    Args:
        data: Data structure to clean (dict, list, str, or other)

    Returns:
        Cleaned data structure

    Example:
        >>> data = {"text": "Line 1\u2028Line 2"}
        >>> cleaned = clean_data_for_json(data)
        >>> cleaned
        {'text': 'Line 1\\nLine 2'}
    """
    if isinstance(data, str):
        # Replace unusual line terminators with standard newline
        return data.replace("\u2028", "\n").replace("\u2029", "\n")
    elif isinstance(data, dict):
        return {key: clean_data_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [clean_data_for_json(item) for item in data]
    else:
        return data
