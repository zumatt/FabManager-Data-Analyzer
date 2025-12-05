"""
Training Data Extraction Module

This module provides functionality to extract training data from the FabManager Open API.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from .api_client import FabManagerAPIClient
from .utils import clean_data_for_json

logger = logging.getLogger(__name__)


def extract_trainings(
    base_url: str,
    api_token: str,
    per_page: int = 100,
    max_pages: Optional[int] = None,
    show_progress: bool = True,
) -> List[Dict]:
    """
    Extract all training data from FabManager.

    Args:
        base_url: Base URL of the FabManager API (e.g., 'https://example-fabmanager.com')
        api_token: API authentication token
        per_page: Number of items per page (default: 100)
        max_pages: Maximum number of pages to fetch (default: None, fetch all)
        show_progress: Whether to show progress in console (default: True)

    Returns:
        List of training records

    Example:
        >>> trainings = extract_trainings(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here'
        ... )
        >>> print(f"Fetched {len(trainings)} trainings")
    """
    logger.info("Starting training data extraction")

    client = FabManagerAPIClient(base_url=base_url, api_token=api_token)

    trainings = client.fetch_all_as_list(
        endpoint="/open_api/v1/trainings",
        data_key="trainings",
        per_page=per_page,
        max_pages=max_pages,
        show_progress=show_progress,
    )

    logger.info(f"Successfully extracted {len(trainings)} trainings")
    return trainings


def save_trainings(
    trainings: List[Dict],
    output_path: Optional[Union[str, Path]] = None,
    add_timestamp: bool = True,
) -> str:
    """
    Save training data to a JSON file.

    Args:
        trainings: List of training records to save
        output_path: Path to save the file. If None, saves to current directory
        add_timestamp: Whether to add timestamp to filename (default: True)

    Returns:
        Path to the saved file

    Example:
        >>> trainings = extract_trainings(base_url, api_token)
        >>> filepath = save_trainings(trainings, output_path='exports/')
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
            filename = f"FabManager_ExportedData_Trainings_{timestamp}.json"
        else:
            filename = "FabManager_ExportedData_Trainings.json"

        filepath = output_dir / filename

    # Clean data to remove unusual line terminators
    logger.info("Cleaning data for JSON export")
    cleaned_data = clean_data_for_json(trainings)

    # Prepare output data
    output_data = {"trainings": cleaned_data}

    # Save to file
    logger.info(f"Saving {len(trainings)} trainings to {filepath}")
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Successfully saved trainings to {filepath}")
    return str(filepath)


def extract_and_save_trainings(
    base_url: str,
    api_token: str,
    output_path: Optional[Union[str, Path]] = None,
    per_page: int = 100,
    max_pages: Optional[int] = None,
    add_timestamp: bool = True,
    show_progress: bool = True,
) -> tuple[List[Dict], str]:
    """
    Extract training data and save it to a file in one operation.

    Args:
        base_url: Base URL of the FabManager API
        api_token: API authentication token
        output_path: Path to save the file (directory or file)
        per_page: Number of items per page (default: 100)
        max_pages: Maximum number of pages to fetch (default: None)
        add_timestamp: Whether to add timestamp to filename (default: True)
        show_progress: Whether to show progress in console (default: True)

    Returns:
        Tuple of (trainings list, filepath)

    Example:
        >>> trainings, filepath = extract_and_save_trainings(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here',
        ...     output_path='exports/'
        ... )
        >>> print(f"Extracted {len(trainings)} trainings and saved to {filepath}")
    """
    logger.info("Starting training extraction and save operation")

    # Extract trainings
    trainings = extract_trainings(
        base_url=base_url,
        api_token=api_token,
        per_page=per_page,
        max_pages=max_pages,
        show_progress=show_progress,
    )

    # Save trainings
    if show_progress:
        print("Saving data...", end="", flush=True)

    filepath = save_trainings(
        trainings=trainings, output_path=output_path, add_timestamp=add_timestamp
    )

    if show_progress:
        print(f"\r✓ Saved {len(trainings)} trainings to file" + " " * 20, flush=True)

    logger.info(f"Completed: {len(trainings)} trainings saved to {filepath}")
    return trainings, filepath
