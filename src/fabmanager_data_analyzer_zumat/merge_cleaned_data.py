"""
Merge cleaned FabManager data from multiple sources.

This module provides functions to merge cleaned machine, training, and reservation data
into a single comprehensive dataset with unified metadata.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Union


def merge_cleaned_data(
    machines_data_path: Optional[str] = None,
    trainings_data_path: Optional[str] = None,
    reservations_machine_data_path: Optional[str] = None,
    reservations_training_data_path: Optional[str] = None,
    output_file: Optional[str] = None,
    data_owner: Optional[str] = None,
    data_steward: Optional[str] = None,
    data_curator: Optional[str] = None,
    data_exported_from: Optional[str] = None,
    license: Optional[str] = None,
    timezone: Optional[str] = None,
) -> Tuple[Dict, str]:
    """
    Merge cleaned FabManager data from multiple sources into a single dataset.

    This function combines cleaned data from machines, trainings, and reservations
    (both machine and training) into a unified JSON structure with comprehensive metadata.

    Args:
        machines_data_path: Path to cleaned machines JSON file (optional)
        trainings_data_path: Path to cleaned trainings JSON file (optional)
        reservations_machine_data_path: Path to cleaned machine reservations JSON file (optional)
        reservations_training_data_path: Path to cleaned training reservations JSON file (optional)
        output_file: Path for the output merged file. If None, generates automatic name
        data_owner: Data owner (optional, if not provided, taken from first file)
        data_steward: Data steward (optional, if not provided, taken from first file)
        data_curator: Data curator (optional, if not provided, taken from first file)
        data_exported_from: Source URL (optional, if not provided, taken from first file)
        license: License information (optional, if not provided, taken from first file)
        timezone: Timezone information (optional, if not provided, taken from first file)

    Returns:
        Tuple of (merged_data_dict, output_filepath)

    Raises:
        ValueError: If fewer than 2 data paths are provided
        FileNotFoundError: If any provided file path doesn't exist
        json.JSONDecodeError: If any file is not valid JSON

    Example:
        >>> merged_data, output_path = merge_cleaned_data(
        ...     machines_data_path='cleaned_machines.json',
        ...     trainings_data_path='cleaned_trainings.json',
        ...     reservations_machine_data_path='cleaned_reservations_machine.json',
        ...     reservations_training_data_path='cleaned_reservations_training.json',
        ...     data_owner='Your Organization Name or Person',
        ...     license='License Name',
        ...     timezone='UTC'
        ... )
        >>> print(f"Merged data saved to: {output_path}")
    """
    # Validate that at least 2 data paths are provided
    provided_paths = [
        machines_data_path,
        trainings_data_path,
        reservations_machine_data_path,
        reservations_training_data_path,
    ]

    if sum(path is not None for path in provided_paths) < 2:
        raise ValueError(
            "At least 2 data paths must be provided. "
            "Please provide at least two of: machines_data_path, trainings_data_path, "
            "reservations_machine_data_path, reservations_training_data_path"
        )

    # Initialize merged data structure
    merged_data = {}
    merged_metadata = {"data_merged_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}

    # Track if we've taken metadata from first file
    metadata_from_first_file = False

    # Helper function to load and extract data
    def load_data_file(file_path: Optional[str], data_key: str, metadata_prefix: str):
        nonlocal metadata_from_first_file

        if file_path is None:
            return None

        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract data array
        data_array = data.get(data_key, [])

        # Extract metadata
        file_metadata = data.get("metadata", {})

        # If this is the first file and user hasn't provided metadata, use file's metadata
        if not metadata_from_first_file:
            if data_owner is None and "data_owner" in file_metadata:
                merged_metadata["data_owner"] = file_metadata["data_owner"]
            if data_steward is None and "data_steward" in file_metadata:
                merged_metadata["data_steward"] = file_metadata["data_steward"]
            if data_curator is None and "data_curator" in file_metadata:
                merged_metadata["data_curator"] = file_metadata["data_curator"]
            if data_exported_from is None and "data_exported_from" in file_metadata:
                merged_metadata["data_exported_from"] = file_metadata[
                    "data_exported_from"
                ]
            if license is None and "license" in file_metadata:
                merged_metadata["license"] = file_metadata["license"]
            if timezone is None and "timezone" in file_metadata:
                merged_metadata["timezone"] = file_metadata["timezone"]

            metadata_from_first_file = True

        # Add specific metadata for this data type
        if "data_exported_at" in file_metadata:
            merged_metadata[f"{metadata_prefix}_data_exported_at"] = file_metadata[
                "data_exported_at"
            ]
        if "data_cleaned_at" in file_metadata:
            merged_metadata[f"{metadata_prefix}_data_cleaned_at"] = file_metadata[
                "data_cleaned_at"
            ]

        return data_array

    # Load machines data
    machines_data = load_data_file(machines_data_path, "machines", "machine")
    if machines_data is not None:
        merged_data["machines"] = machines_data

    # Load trainings data
    trainings_data = load_data_file(trainings_data_path, "trainings", "training")
    if trainings_data is not None:
        merged_data["trainings"] = trainings_data

    # Load machine reservations data
    reservations_machine_data = load_data_file(
        reservations_machine_data_path, "reservations", "reservations_machine"
    )
    if reservations_machine_data is not None:
        merged_data["reservations_machine"] = reservations_machine_data

    # Load training reservations data
    reservations_training_data = load_data_file(
        reservations_training_data_path, "reservations", "reservations_training"
    )
    if reservations_training_data is not None:
        merged_data["reservations_training"] = reservations_training_data

    # Override with user-provided metadata if given
    if data_owner is not None:
        merged_metadata["data_owner"] = data_owner
    if data_steward is not None:
        merged_metadata["data_steward"] = data_steward
    if data_curator is not None:
        merged_metadata["data_curator"] = data_curator
    if data_exported_from is not None:
        merged_metadata["data_exported_from"] = data_exported_from
    if license is not None:
        merged_metadata["license"] = license
    if timezone is not None:
        merged_metadata["timezone"] = timezone

    # Generate output filename if not provided
    output_path: Union[str, Path]
    if output_file is None:
        timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M")
        output_path = Path.cwd() / f"FabManager_Merged_Data_{timestamp}.json"
    else:
        output_path = Path(output_file)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Build final output structure with nested data
    output_data = {"metadata": merged_metadata, "data": {}}

    # Add data sections in the correct order under 'data' key
    if "machines" in merged_data:
        output_data["data"]["machines"] = merged_data["machines"]
    if "trainings" in merged_data:
        output_data["data"]["trainings"] = merged_data["trainings"]
    if "reservations_machine" in merged_data:
        output_data["data"]["reservations_machine"] = merged_data[
            "reservations_machine"
        ]
    if "reservations_training" in merged_data:
        output_data["data"]["reservations_training"] = merged_data[
            "reservations_training"
        ]

    # Write output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return output_data, str(output_path)


__all__ = [
    "merge_cleaned_data",
]
