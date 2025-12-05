"""
Reservation Data Extraction Module

This module provides functionality to extract reservation data from the FabManager Open API.
Includes functionality to divide reservations by type (Machine, Training, Event).
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

from .api_client import FabManagerAPIClient
from .utils import clean_data_for_json, sanitize_filename

logger = logging.getLogger(__name__)


def extract_reservations(
    base_url: str,
    api_token: str,
    per_page: int = 100,
    max_pages: Optional[int] = None,
    show_progress: bool = True,
) -> List[Dict]:
    """
    Extract all reservation data from FabManager.

    Args:
        base_url: Base URL of the FabManager API (e.g., 'https://example-fabmanager.com')
        api_token: API authentication token
        per_page: Number of items per page (default: 100)
        max_pages: Maximum number of pages to fetch (default: None, fetch all)
        show_progress: Whether to show progress in console (default: True)

    Returns:
        List of reservation records

    Example:
        >>> reservations = extract_reservations(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here'
        ... )
        >>> print(f"Fetched {len(reservations)} reservations")
    """
    logger.info("Starting reservation data extraction")

    client = FabManagerAPIClient(base_url=base_url, api_token=api_token)

    reservations = client.fetch_all_as_list(
        endpoint="/open_api/v1/reservations",
        data_key="reservations",
        per_page=per_page,
        max_pages=max_pages,
        show_progress=show_progress,
    )

    logger.info(f"Successfully extracted {len(reservations)} reservations")
    return reservations


def divide_reservations_by_type(reservations: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Divide reservations into groups by reservable_type.

    Args:
        reservations: List of reservation objects

    Returns:
        Dictionary mapping reservation types to lists of reservations

    Example:
        >>> reservations = extract_reservations(base_url, api_token)
        >>> groups = divide_reservations_by_type(reservations)
        >>> for rtype, items in groups.items():
        ...     print(f"{rtype}: {len(items)} reservations")
    """
    logger.info("Dividing reservations by type...")

    groups = defaultdict(list)
    for reservation in reservations:
        rtype = (
            reservation.get("reservable_type") or reservation.get("type") or "unknown"
        )
        if not isinstance(rtype, str):
            rtype = str(rtype)
        groups[rtype].append(reservation)

    logger.info(f"Divided into {len(groups)} reservation types")
    for rtype, items in groups.items():
        logger.info(f"  - {rtype}: {len(items)} reservations")

    return dict(groups)


def save_reservations(
    reservations: List[Dict],
    output_path: Optional[Union[str, Path]] = None,
    add_timestamp: bool = True,
    divide_by_type: bool = False,
) -> Union[str, Dict[str, str]]:
    """
    Save reservation data to JSON file(s).

    Args:
        reservations: List of reservation records to save
        output_path: Path to save the file(s). If None, saves to current directory
        add_timestamp: Whether to add timestamp to filename (default: True)
        divide_by_type: Whether to divide reservations by type into separate files (default: False)

    Returns:
        If divide_by_type is False: Path to the saved file (str)
        If divide_by_type is True: Dictionary mapping types to file paths

    Example:
        >>> reservations = extract_reservations(base_url, api_token)
        >>> # Save all together
        >>> filepath = save_reservations(reservations, output_path='exports/')
        >>> # Save divided by type
        >>> filepaths = save_reservations(reservations, output_path='exports/', divide_by_type=True)
    """
    # Prepare output path
    if output_path is None:
        output_dir = Path.cwd()
    else:
        output_dir = Path(output_path)

    if divide_by_type:
        # Divide and save by type
        return _save_reservations_divided(reservations, output_dir, add_timestamp)
    else:
        # Save all together
        return _save_reservations_combined(reservations, output_dir, add_timestamp)


def _save_reservations_combined(
    reservations: List[Dict], output_dir: Path, add_timestamp: bool
) -> str:
    """
    Save all reservations to a single JSON file.

    Args:
        reservations: List of reservation records
        output_dir: Directory to save the file
        add_timestamp: Whether to add timestamp to filename

    Returns:
        Path to the saved file
    """
    # Create directory if it doesn't exist
    if output_dir.suffix:  # If it's a file path
        output_dir.parent.mkdir(parents=True, exist_ok=True)
        filepath = output_dir
    else:  # If it's a directory path
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        if add_timestamp:
            timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M")
            filename = f"FabManager_ExportedData_Reservations_{timestamp}.json"
        else:
            filename = "FabManager_ExportedData_Reservations.json"

        filepath = output_dir / filename

    # Clean data to remove unusual line terminators
    logger.info("Cleaning data for JSON export")
    cleaned_data = clean_data_for_json(reservations)

    # Prepare output data
    output_data = {"reservations": cleaned_data}

    # Save to file
    logger.info(f"Saving {len(reservations)} reservations to {filepath}")
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    logger.info(f"Successfully saved reservations to {filepath}")
    return str(filepath)


def _save_reservations_divided(
    reservations: List[Dict], output_dir: Path, add_timestamp: bool
) -> Dict[str, str]:
    """
    Save reservations divided by type to separate JSON files.

    Args:
        reservations: List of reservation records
        output_dir: Directory to save the files
        add_timestamp: Whether to add timestamp to filenames

    Returns:
        Dictionary mapping reservation types to file paths
    """
    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Divide reservations by type
    groups = divide_reservations_by_type(reservations)

    # Generate timestamp for the files
    timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M")

    # Save each type as a separate file
    filepaths = {}
    for rtype, items in groups.items():
        # Generate filename
        if add_timestamp:
            filename = f"FabManager_ExportedData_Reservations_{sanitize_filename(rtype)}_{timestamp}.json"
        else:
            filename = (
                f"FabManager_ExportedData_Reservations_{sanitize_filename(rtype)}.json"
            )

        filepath = output_dir / filename

        # Clean data before saving
        logger.info(f"Cleaning {rtype} reservation data for JSON export")
        cleaned_items = clean_data_for_json(items)

        # Prepare output data
        output_data = {"reservations": cleaned_items}

        # Save to file
        logger.info(f"Saving {len(items)} {rtype} reservations to {filename}")
        with open(filepath, "w", encoding="utf-8", newline="\n") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        filepaths[rtype] = str(filepath)
        logger.info(f"  - {rtype}: {len(items)} items saved to {filename}")

    logger.info(f"Successfully created {len(groups)} reservation files by type")
    return filepaths


def extract_and_save_reservations(
    base_url: str,
    api_token: str,
    output_path: Optional[Union[str, Path]] = None,
    per_page: int = 100,
    max_pages: Optional[int] = None,
    add_timestamp: bool = True,
    divide_by_type: bool = False,
    show_progress: bool = True,
) -> tuple[List[Dict], Union[str, Dict[str, str]]]:
    """
    Extract reservation data and save it to file(s) in one operation.

    Args:
        base_url: Base URL of the FabManager API
        api_token: API authentication token
        output_path: Path to save the file(s) (directory or file)
        per_page: Number of items per page (default: 100)
        max_pages: Maximum number of pages to fetch (default: None)
        add_timestamp: Whether to add timestamp to filename(s) (default: True)
        divide_by_type: Whether to divide by type into separate files (default: False)
        show_progress: Whether to show progress in console (default: True)

    Returns:
        Tuple of (reservations list, filepath(s))
        If divide_by_type is False: filepath is a string
        If divide_by_type is True: filepath is a dict mapping types to paths

    Example:
        >>> # Save all together
        >>> reservations, filepath = extract_and_save_reservations(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here',
        ...     output_path='exports/'
        ... )
        >>> print(f"Saved {len(reservations)} reservations to {filepath}")

        >>> # Save divided by type
        >>> reservations, filepaths = extract_and_save_reservations(
        ...     base_url='https://example-fabmanager.com',
        ...     api_token='your_token_here',
        ...     output_path='exports/',
        ...     divide_by_type=True
        ... )
        >>> for rtype, path in filepaths.items():
        ...     print(f"{rtype} saved to {path}")
    """
    logger.info("Starting reservation extraction and save operation")

    # Extract reservations
    reservations = extract_reservations(
        base_url=base_url,
        api_token=api_token,
        per_page=per_page,
        max_pages=max_pages,
        show_progress=show_progress,
    )

    # Save reservations
    if show_progress:
        if divide_by_type:
            print("Dividing by type and saving...", end="", flush=True)
        else:
            print("Saving data...", end="", flush=True)

    filepaths = save_reservations(
        reservations=reservations,
        output_path=output_path,
        add_timestamp=add_timestamp,
        divide_by_type=divide_by_type,
    )

    if show_progress:
        if divide_by_type:
            num_types = len(filepaths) if isinstance(filepaths, dict) else 1
            print(
                f"\r✓ Saved {len(reservations)} reservations to {num_types} files"
                + " " * 20,
                flush=True,
            )
        else:
            print(
                f"\r✓ Saved {len(reservations)} reservations to file" + " " * 20,
                flush=True,
            )

    logger.info(f"Completed: {len(reservations)} reservations extracted and saved")
    return reservations, filepaths
