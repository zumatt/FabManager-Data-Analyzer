"""
Machine Data Extraction Module

This module provides functionality to extract machine data from the FabManager Open API.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from .api_client import FabManagerAPIClient
from .utils import clean_data_for_json

logger = logging.getLogger(__name__)


def extract_machines(
    base_url: str,
    api_token: str,
    per_page: int = 100,
    max_pages: Optional[int] = None,
    show_progress: bool = True,
) -> List[Dict]:
    """
    Extract all machine data from FabManager.

    Args:
        base_url: Base URL of the FabManager API (e.g., 'https://example-fabmanager.com')
        api_token: API authentication token
        per_page: Number of items per page (default: 100)
        max_pages: Maximum number of pages to fetch (default: None, fetch all)
        show_progress: Whether to show progress in console (default: True)

    Returns:
        List of machine records

    Example:
        >>> machines = extract_machines(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here'
        ... )
        >>> print(f"Fetched {len(machines)} machines")
    """
    logger.info("Starting machine data extraction")

    client = FabManagerAPIClient(base_url=base_url, api_token=api_token)

    machines = client.fetch_all_as_list(
        endpoint="/open_api/v1/machines",
        data_key="machines",
        per_page=per_page,
        max_pages=max_pages,
        show_progress=show_progress,
    )

    logger.info(f"Successfully extracted {len(machines)} machines")
    return machines


def save_machines(
    machines: List[Dict],
    output_path: Optional[Union[str, Path]] = None,
    add_timestamp: bool = True,
) -> str:
    """
    Save machine data to a JSON file.

    Args:
        machines: List of machine records to save
        output_path: Path to save the file. If None, saves to current directory
        add_timestamp: Whether to add timestamp to filename (default: True)

    Returns:
        Path to the saved file

    Example:
        >>> machines = extract_machines(base_url, api_token)
        >>> filepath = save_machines(machines, output_path='exports/')
        >>> print(f"Saved to {filepath}")
    """
    # Prepare output path
    if output_path is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_path)

    # Create directory if it doesn't exist
    if output_dir.suffix:  # If it's a file path
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        filepath = output_dir
    else:  # If it's a directory path
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        if add_timestamp:
            timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M")
            filename = f"FabManager_ExportedData_Machines_{timestamp}.json"
        else:
            filename = "FabManager_ExportedData_Machines.json"

        filepath = output_dir / filename

    # Clean data to remove unusual line terminators
    logger.info("Cleaning data for JSON export")
    cleaned_data = clean_data_for_json(machines)

    # Prepare output data
    output_data = {"machines": cleaned_data}

    # Save to file
    logger.info(f"Saving {len(machines)} machines to {filepath}")
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Successfully saved machines to {filepath}")
    return str(filepath)


def extract_and_save_machines(
    base_url: str,
    api_token: str,
    output_path: Optional[Union[str, Path]] = None,
    per_page: int = 100,
    max_pages: Optional[int] = None,
    add_timestamp: bool = True,
    show_progress: bool = True,
) -> tuple[List[Dict], str]:
    """
    Extract machine data and save it to a file in one operation.

    Args:
        base_url: Base URL of the FabManager API
        api_token: API authentication token
        output_path: Path to save the file (directory or file)
        per_page: Number of items per page (default: 100)
        max_pages: Maximum number of pages to fetch (default: None)
        add_timestamp: Whether to add timestamp to filename (default: True)
        show_progress: Whether to show progress in console (default: True)

    Returns:
        Tuple of (machines list, filepath)

    Example:
        >>> machines, filepath = extract_and_save_machines(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here',
        ...     output_path='exports/'
        ... )
        >>> print(f"Extracted {len(machines)} machines and saved to {filepath}")
    """
    logger.info("Starting machine extraction and save operation")

    # Extract machines
    machines = extract_machines(
        base_url=base_url,
        api_token=api_token,
        per_page=per_page,
        max_pages=max_pages,
        show_progress=show_progress,
    )

    # Save machines
    if show_progress:
        print("Saving data...", end="", flush=True)

    filepath = save_machines(
        machines=machines, output_path=output_path, add_timestamp=add_timestamp
    )

    if show_progress:
        print(f"\r✓ Saved {len(machines)} machines to file" + " " * 20, flush=True)

    logger.info(f"Completed: {len(machines)} machines saved to {filepath}")
    return machines, filepath
