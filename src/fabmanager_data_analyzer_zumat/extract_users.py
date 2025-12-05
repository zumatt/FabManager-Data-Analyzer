"""
Extract user data from FabManager API.

This module provides functions to extract user data from the FabManager Open API
and save it to JSON files with timestamped filenames.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .api_client import FabManagerAPIClient
from .utils import clean_data_for_json, sanitize_filename


def extract_users(
    base_url: str, api_token: str, show_progress: bool = True
) -> List[Dict]:
    """
    Extract all users from the FabManager API.

    This function fetches all user records from the FabManager Open API endpoint
    /open_api/v1/users. It handles pagination automatically and returns all users
    as a list of dictionaries.

    Args:
        base_url: The base URL of the FabManager instance (e.g., 'https://example-fabmanager.com')
        api_token: Your FabManager API authentication token
        show_progress: Whether to display progress information during extraction (default: True)

    Returns:
        A list of dictionaries, where each dictionary contains user data

    Example:
        >>> users = extract_users(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here'
        ... )
        >>> print(f"Extracted {len(users)} users")
    """
    client = FabManagerAPIClient(base_url=base_url, api_token=api_token)

    users = client.fetch_all_as_list(
        endpoint="/open_api/v1/users",
        data_key="users",
        per_page=100,
        show_progress=show_progress,
    )

    return users


def save_users(
    users: List[Dict], output_path: str = ".", custom_filename: Optional[str] = None
) -> str:
    """
    Save user data to a JSON file.

    Saves the provided user data to a JSON file with a timestamped filename.
    The data is cleaned to remove unusual Unicode line terminators before saving.

    Args:
        users: List of user dictionaries to save
        output_path: Directory where the file should be saved (default: current directory)
        custom_filename: Optional custom filename (without extension). If not provided,
                        uses format 'FabManager_ExportedData_Users_DD_MM_YYYY_HH-MM.json'

    Returns:
        The full path to the saved file as a string

    Example:
        >>> users = extract_users(base_url='...', api_token='...')
        >>> filepath = save_users(users, output_path='exports/')
        >>> print(f"Saved to {filepath}")
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    if custom_filename:
        filename = f"{sanitize_filename(custom_filename)}.json"
    else:
        timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M")
        filename = f"FabManager_ExportedData_Users_{timestamp}.json"

    filepath = output_dir / filename

    # Clean data to remove unusual line terminators
    cleaned_users = clean_data_for_json(users)

    # Prepare output data
    output_data = {"users": cleaned_users}

    # Save to file
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return str(filepath)


def extract_and_save_users(
    base_url: str,
    api_token: str,
    output_path: str = ".",
    custom_filename: Optional[str] = None,
    show_progress: bool = True,
) -> Tuple[List[Dict], str]:
    """
    Extract users from FabManager API and save to a JSON file.

    This is a convenience function that combines extract_users() and save_users()
    into a single operation. It extracts all user data and immediately saves it
    to a timestamped JSON file.

    Args:
        base_url: The base URL of the FabManager instance
        api_token: Your FabManager API authentication token
        output_path: Directory where the file should be saved (default: current directory)
        custom_filename: Optional custom filename (without extension)
        show_progress: Whether to display progress information during extraction (default: True)

    Returns:
        A tuple containing:
        - List of user dictionaries
        - Path to the saved file as a string

    Example:
        >>> users, filepath = extract_and_save_users(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here',
        ...     output_path='exports/'
        ... )
        >>> print(f"Extracted {len(users)} users")
        >>> print(f"Saved to {filepath}")

    Note:
        This function displays real-time progress during extraction, showing the number
        of items fetched and the current page being processed.
    """
    # Extract users
    users = extract_users(
        base_url=base_url, api_token=api_token, show_progress=show_progress
    )

    # Save to file
    filepath = save_users(
        users=users, output_path=output_path, custom_filename=custom_filename
    )

    return users, filepath


__all__ = ["extract_users", "save_users", "extract_and_save_users"]
