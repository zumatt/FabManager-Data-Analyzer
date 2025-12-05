"""
Clean and transform training reservation data from FabManager exports.

This module provides functions to clean and prepare training reservation data for analysis
or publication as Open Data. It extracts relevant fields and creates references to the
trainings dataset.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple, Union


def extract_timestamp_from_filename(filename: str) -> Optional[str]:
    """
    Extract timestamp from FabManager export filename.

    Expected format: FabManager_ExportedData_*_DD_MM_YYYY_HH-MM.json

    Args:
        filename: The filename to extract timestamp from

    Returns:
        ISO format timestamp string (YYYY-MM-DDTHH:MM) or None if not found

    Example:
        >>> extract_timestamp_from_filename('FabManager_ExportedData_Reservations_Training_01_01_2025_00-00.json')
        '2025-01-01T00:00'
    """
    # Pattern: DD_MM_YYYY_HH-MM
    pattern = r"(\d{2})_(\d{2})_(\d{4})_(\d{2})-(\d{2})"
    match = re.search(pattern, filename)

    if match:
        day, month, year, hour, minute = match.groups()
        try:
            # Convert to ISO format: YYYY-MM-DDTHH:MM
            return f"{year}-{month}-{day}T{hour}:{minute}"
        except ValueError:
            return None

    return None


def process_timestamp_field(
    timestamp: Optional[str], mode: Literal["all", "only_date", "remove"]
) -> Optional[str]:
    """
    Process timestamp field based on the specified mode.

    Args:
        timestamp: ISO format timestamp string
        mode: Processing mode - 'all' keeps full timestamp, 'only_date' keeps only date,
              'remove' returns None

    Returns:
        Processed timestamp or None

    Example:
        >>> process_timestamp_field('2025-01-01T00:00:00Z', 'only_date')
        '2025-01-01'
    """
    if mode == "remove" or not timestamp:
        return None

    if mode == "only_date":
        # Extract only the date part (YYYY-MM-DD)
        try:
            return timestamp.split("T")[0]
        except (IndexError, AttributeError):
            return timestamp

    # mode == 'all'
    return timestamp


def clean_reservation_record(
    reservation: Dict,
    updated_at_mode: Literal["all", "only_date", "remove"] = "all",
    created_at_mode: Literal["all", "only_date", "remove"] = "all",
    create_linked_data: bool = False,
    base_domain: Optional[str] = None,
) -> Optional[Dict]:
    """
    Clean a single training reservation record.

    Args:
        reservation: Reservation record to clean
        updated_at_mode: How to handle updated_at field ('all', 'only_date', 'remove')
        created_at_mode: How to handle created_at field ('all', 'only_date', 'remove')
        create_linked_data: If True, create 'training_url' field with full URL
        base_domain: Base domain for creating linked data URLs (required if create_linked_data=True)

    Returns:
        Cleaned reservation record or None if invalid

    Example:
        >>> reservation = {
        ...     'id': 00000,
        ...     'reservable_id': 0,
        ...     'reservable_type': 'Training',
        ...     'updated_at': '2025-01-01T08:00:00.000+01:00',
        ...     'created_at': '2025-01-01T08:00:00.000+01:00',
        ...     'user': {'group': {'name': 'Student'}},
        ...     'reservable': {'id': 1, 'slug': '3d-printing-basics'},
        ...     'reserved_slots': [{'canceled_at': None}]
        ... }
        >>> cleaned = clean_reservation_record(reservation)
        >>> cleaned['user_group']
        'Student'
    """
    # Validate required fields
    if not reservation.get("reservable_id"):
        return None

    # Only process Training reservations
    if reservation.get("reservable_type") != "Training":
        return None

    # Start building cleaned record (without ID)
    cleaned = {}

    # Process timestamps
    if "updated_at" in reservation:
        processed = process_timestamp_field(reservation["updated_at"], updated_at_mode)
        if processed is not None:
            cleaned["updated_at"] = processed

    if "created_at" in reservation:
        processed = process_timestamp_field(reservation["created_at"], created_at_mode)
        if processed is not None:
            cleaned["created_at"] = processed

    # Extract user group name
    user = reservation.get("user", {})
    group = user.get("group", {})
    if group.get("name"):
        cleaned["user_group"] = group["name"]

    # Extract reservable information (training reference)
    reservable = reservation.get("reservable", {})
    if reservable.get("id"):
        cleaned["training_id"] = reservable["id"]

        # Create linked data URL if requested
        if create_linked_data and base_domain and reservable.get("slug"):
            base_domain = base_domain.rstrip("/")
            slug = reservable["slug"].lstrip("/")
            cleaned["training_url"] = f"{base_domain}/{slug}"

    # Process reserved slots - determine if canceled
    reserved_slots = reservation.get("reserved_slots", [])
    if reserved_slots:
        # Check if any slot is canceled
        canceled = any(slot.get("canceled_at") is not None for slot in reserved_slots)
        cleaned["canceled"] = str(canceled)

    return cleaned


def clean_reservations_training_data(
    input_file: str,
    output_file: Optional[str] = None,
    updated_at_mode: Literal["all", "only_date", "remove"] = "all",
    created_at_mode: Literal["all", "only_date", "remove"] = "all",
    create_linked_data: bool = False,
    base_domain: Optional[str] = None,
    data_owner: Optional[str] = None,
    data_steward: Optional[str] = None,
    data_curator: Optional[str] = None,
    data_exported_from: Optional[str] = None,
    data_exported_at: Optional[str] = None,
    license: Optional[str] = None,
) -> Tuple[List[Dict], str]:
    """
    Clean and transform training reservation data from FabManager export.

    This function reads a FabManager reservation export file, filters for training
    reservations only, and applies various cleaning operations.

    Args:
        input_file: Path to the input JSON file
        output_file: Path for the output file. If None, generates automatic name
        updated_at_mode: How to handle updated_at timestamps:
                        - 'all': Keep full ISO timestamp
                        - 'only_date': Keep only date (YYYY-MM-DD)
                        - 'remove': Remove the field entirely
        created_at_mode: How to handle created_at timestamps (same options as updated_at_mode)
        create_linked_data: If True, create 'training_url' field with full URL to training page
        base_domain: Base domain for linked data URLs (e.g., 'https://example-fabmanager.com').
                    Required when create_linked_data=True
        data_owner: Organization or person who owns the data (optional, added to metadata)
        data_steward: Person responsible for data quality (optional, added to metadata)
        data_curator: Person who prepared/cleaned the data (optional, added to metadata)
        data_exported_from: URL where data was exported from (optional, added to metadata)
        data_exported_at: Date and time when the original data was exported (optional, added to metadata).
                         If not provided, automatically extracted from input filename if it follows
                         the FabManager export format: *_DD_MM_YYYY_HH-MM.json
        license: License under which the data is published (optional, added to metadata)

    Returns:
        Tuple of (list of cleaned reservation records, path to output file)

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If create_linked_data=True but base_domain is not provided
        json.JSONDecodeError: If input file is not valid JSON

    Example:
        >>> reservations, path = clean_reservations_training_data(
        ...     input_file='your_input_file.json',
        ...     updated_at_mode='only_date',
        ...     created_at_mode='only_date',
        ...     create_linked_data=True,
        ...     base_domain='https://example-fabmanager.com',
        ...     data_owner='Your Organization Name or Person',
        ...     license='License Name'
        ... )
        >>> len(reservations)
        123456
    """
    # Convert to Path objects
    input_path = Path(input_file)

    # Extract timestamp from filename if data_exported_at not provided
    if data_exported_at is None:
        data_exported_at = extract_timestamp_from_filename(input_path.name)

    # Check if input file exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Validate base_domain requirement
    if create_linked_data and not base_domain:
        raise ValueError("base_domain is required when create_linked_data=True")

    # Read input file
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract reservations array
    if isinstance(data, dict) and "reservations" in data:
        reservations = data["reservations"]
    elif isinstance(data, list):
        reservations = data
    else:
        raise ValueError(
            "Input file must contain a 'reservations' key or be a list of reservations"
        )

    # Clean each reservation record
    cleaned_reservations = []
    for reservation in reservations:
        cleaned = clean_reservation_record(
            reservation=reservation,
            updated_at_mode=updated_at_mode,
            created_at_mode=created_at_mode,
            create_linked_data=create_linked_data,
            base_domain=base_domain,
        )
        if cleaned is not None:
            cleaned_reservations.append(cleaned)

    # Generate output filename if not provided
    output_path: Union[str, Path]
    if output_file is None:
        timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M")
        suffix = "linked" if create_linked_data else "cleaned"
        output_path = (
            input_path.parent
            / f"FabManager_Reservations_Training_Cleaned_{suffix}_{timestamp}.json"
        )
    else:
        output_path = Path(output_file)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Prepare output data structure
    output_data: Dict = {"reservations": cleaned_reservations}

    # Add metadata if any optional fields are provided
    metadata = {}

    if data_owner is not None:
        metadata["data_owner"] = data_owner
    if data_steward is not None:
        metadata["data_steward"] = data_steward
    if data_curator is not None:
        metadata["data_curator"] = data_curator
    if data_exported_from is not None:
        metadata["data_exported_from"] = data_exported_from
    if data_exported_at is not None:
        metadata["data_exported_at"] = data_exported_at
    if license is not None:
        metadata["license"] = license

    # Add cleaning timestamp
    metadata["data_cleaned_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    if metadata:
        output_data["metadata"] = metadata

    # Write output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return cleaned_reservations, str(output_path)


__all__ = [
    "clean_reservations_training_data",
    "clean_reservation_record",
    "process_timestamp_field",
    "extract_timestamp_from_filename",
]
