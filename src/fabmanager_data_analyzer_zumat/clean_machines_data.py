"""
Clean and transform machine data from FabManager exports.

This module provides functions to clean and prepare machine data for analysis or publication
as Open Data. It offers various cleaning options including filtering disabled machines,
creating linked data, handling timestamps, and cleaning HTML content.
"""

import json
import re
from datetime import datetime
from html.parser import HTMLParser
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
        >>> extract_timestamp_from_filename('FabManager_ExportedData_Machines_01_01_2025_00-00.json')
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


class HTMLLinkExtractor(HTMLParser):
    """
    Custom HTML parser to extract text while preserving external links.

    This parser removes all HTML tags but keeps external links in a readable format,
    converting <a href="url">text</a> to "text (url)".
    """

    def __init__(self):
        super().__init__()
        self.result = []
        self.current_link = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        """Handle opening tags, capturing link URLs."""
        if tag == "a":
            # Extract href attribute
            for attr_name, attr_value in attrs:
                if attr_name == "href":
                    self.current_link = attr_value
                    break

    def handle_endtag(self, tag):
        """Handle closing tags, formatting links."""
        if tag == "a" and self.current_link:
            # Add the link in format: text (url)
            link_text = "".join(self.current_text).strip()
            if link_text:
                self.result.append(f"{link_text} ({self.current_link})")
            self.current_link = None
            self.current_text = []

    def handle_data(self, data):
        """Handle text content."""
        if self.current_link is not None:
            # We're inside a link, collect the text
            self.current_text.append(data)
        else:
            # Regular text, add it directly
            self.result.append(data)

    def get_text(self):
        """Get the cleaned text with preserved links."""
        return "".join(self.result).strip()


def clean_html_keep_links(html_content: Optional[str]) -> str:
    """
    Clean HTML content while preserving external links.

    Removes all HTML tags but converts links to a readable format:
    <a href="https://example.com">Click here</a> becomes "Click here (https://example.com)"

    Args:
        html_content: HTML string to clean, or None

    Returns:
        Cleaned text with links preserved in readable format

    Example:
        >>> html = '<p>Visit <a href="https://example.com">our site</a> for more.</p>'
        >>> clean_html_keep_links(html)
        'Visit our site (https://example.com) for more.'
    """
    if not html_content:
        return ""

    parser = HTMLLinkExtractor()
    try:
        parser.feed(html_content)
        text = parser.get_text()
        # Clean up multiple spaces and newlines
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    except Exception:
        # If parsing fails, fall back to simple tag removal
        text = re.sub(r"<[^>]+>", "", html_content)
        return re.sub(r"\s+", " ", text).strip()


def process_timestamp_field(
    value: Optional[str], mode: Literal["all", "only_date", "remove"]
) -> Optional[str]:
    """
    Process timestamp fields according to the specified mode.

    Args:
        value: Timestamp string (ISO format) or None
        mode: Processing mode:
            - 'all': Keep the full timestamp as-is
            - 'only_date': Extract only the date part (YYYY-MM-DD)
            - 'remove': Return None (field will be removed)

    Returns:
        Processed timestamp value or None

    Example:
        >>> process_timestamp_field('2025-01-01T00:00:00Z', 'only_date')
        '2025-01-01'
        >>> process_timestamp_field('2025-01-01T00:00:00Z', 'remove')
        None
    """
    if mode == "remove":
        return None

    if mode == "only_date" and value:
        # Extract date part from ISO timestamp
        try:
            # Handle various ISO format variations
            date_part = value.split("T")[0]
            return date_part
        except Exception:
            return value

    # mode == 'all' or any other case
    return value


def create_linked_data_uri(
    slug: str, base_domain: str = "https://example-fabmanager.com"
) -> str:
    """
    Create a full URI for linked data from a machine slug.

    Args:
        slug: Machine slug (e.g., 'laser-cutter')
        base_domain: Base domain of the FabManager instance

    Returns:
        Full URI for the machine

    Example:
        >>> create_linked_data_uri('laser-cutter', 'https://example-fabmanager.com')
        'https://example-fabmanager.com/laser-cutter'
    """
    base_domain = base_domain.rstrip("/")
    slug = slug.lstrip("/")
    return f"{base_domain}/{slug}"


def clean_machine_record(
    machine: Dict,
    include_disabled: bool = True,
    create_linked_data: bool = False,
    base_domain: Optional[str] = None,
    updated_at_mode: Literal["all", "only_date", "remove"] = "all",
    created_at_mode: Literal["all", "only_date", "remove"] = "all",
) -> Optional[Dict]:
    """
    Clean a single machine record according to specified options.

    Args:
        machine: Machine data dictionary
        include_disabled: If False, returns None for disabled machines and removes 'disabled' field
        create_linked_data: If True, converts slug to full URL and removes slug field;
                           if False, removes slug field. Requires base_domain when True.
        base_domain: Base domain for creating linked data URIs (required if create_linked_data=True)
        updated_at_mode: How to handle updated_at field ('all', 'only_date', 'remove')
        created_at_mode: How to handle created_at field ('all', 'only_date', 'remove')

    Returns:
        Cleaned machine dictionary, or None if machine should be filtered out

    Raises:
        ValueError: If create_linked_data=True but base_domain is not provided

    Raises:
        ValueError: If create_linked_data=True but base_domain is not provided

    Example:
        >>> machine = {
        ...     'id': 1,
        ...     'name': 'Laser Cutter',
        ...     'slug': 'laser-cutter',
        ...     'disabled': False,
        ...     'description': '<p>A <a href="http://example.com">great</a> machine</p>',
        ...     'spec': '<ul><li>Power: 100W</li></ul>',
        ...     'created_at': '2025-01-01T00:00:00Z',
        ...     'updated_at': '2025-01-01T00:00:00Z'
        ... }
        >>> cleaned = clean_machine_record(
        ...     machine,
        ...     create_linked_data=True,
        ...     base_domain='https://example-fabmanager.com',
        ...     created_at_mode='only_date'
        ... )
        >>> cleaned['url']
        'https://example-fabmanager.com/laser-cutter'
        >>> cleaned['created_at']
        '2025-01-01'
        >>> 'id' in cleaned
        False
    """
    # Validate parameters
    if create_linked_data and not base_domain:
        raise ValueError(
            "base_domain is required when create_linked_data=True. "
            "Please provide the base URL of your FabManager instance."
        )

    # Filter out disabled machines if requested
    if not include_disabled and machine.get("disabled", False):
        return None

    # Create a copy to avoid modifying the original
    cleaned = machine.copy()

    # Remove ID field
    if "id" in cleaned:
        del cleaned["id"]

    # Remove disabled field when keeping only enabled machines
    if not include_disabled and "disabled" in cleaned:
        del cleaned["disabled"]

    # Handle slug field
    if "slug" in cleaned:
        if create_linked_data:
            # Convert slug to full URL and add as new field
            cleaned["url"] = create_linked_data_uri(cleaned["slug"], base_domain or "")
            # Remove the slug field when creating linked data
            del cleaned["slug"]
        else:
            # Remove slug field
            del cleaned["slug"]

    # Handle description field
    if "description" in cleaned:
        cleaned["description"] = clean_html_keep_links(cleaned["description"])

    # Handle spec field
    if "spec" in cleaned:
        cleaned["spec"] = clean_html_keep_links(cleaned["spec"])

    # Handle created_at field
    if "created_at" in cleaned:
        processed_value = process_timestamp_field(
            cleaned["created_at"], created_at_mode
        )
        if processed_value is None:
            del cleaned["created_at"]
        else:
            cleaned["created_at"] = processed_value

    # Handle updated_at field
    if "updated_at" in cleaned:
        processed_value = process_timestamp_field(
            cleaned["updated_at"], updated_at_mode
        )
        if processed_value is None:
            del cleaned["updated_at"]
        else:
            cleaned["updated_at"] = processed_value

    return cleaned


def clean_machines_data(
    input_file: str,
    output_file: Optional[str] = None,
    include_disabled: bool = True,
    create_linked_data: bool = False,
    base_domain: Optional[str] = None,
    updated_at_mode: Literal["all", "only_date", "remove"] = "all",
    created_at_mode: Literal["all", "only_date", "remove"] = "all",
    data_owner: Optional[str] = None,
    data_steward: Optional[str] = None,
    data_curator: Optional[str] = None,
    data_exported_from: Optional[str] = None,
    data_exported_at: Optional[str] = None,
    license: Optional[str] = None,
) -> Tuple[List[Dict], str]:
    """
    Clean machine data from an exported JSON file.

    This function reads a FabManager machine export file, applies various cleaning
    operations, and saves the cleaned data to a new file.

    Cleaning options:
    - Filter disabled machines and remove 'disabled' field when keeping only enabled
    - Create linked data URIs (requires base_domain) or remove slug field
    - Control timestamp field formatting (full, date-only, or remove)
    - Clean HTML from description and spec fields while preserving links

    Args:
        input_file: Path to the input JSON file containing machine data
        output_file: Path for the output file. If None, generates automatic name
        include_disabled: If True, include all machines; if False, exclude disabled machines
                         and remove 'disabled' field from output
        create_linked_data: If True, add URL field from slug and remove slug field;
                           if False, remove slug field. When True, base_domain is required.
        base_domain: Base domain for creating linked data URIs. Required when create_linked_data=True.
                    Example: 'https://example-fabmanager.com'
        updated_at_mode: How to handle updated_at timestamps:
            - 'all': Keep full timestamp
            - 'only_date': Keep only date part (YYYY-MM-DD)
            - 'remove': Remove field entirely
        created_at_mode: How to handle created_at timestamps (same options as updated_at_mode)
        data_owner: Data owner name/organization (optional, added to metadata)
        data_steward: Data steward name (optional, added to metadata)
        data_curator: Data curator name (optional, added to metadata)
        data_exported_from: Source system/URL where data was exported from (optional, added to metadata)
        data_exported_at: Date and time when the original data was exported (optional, added to metadata).
                         If not provided, automatically extracted from input filename if it follows the
                         FabManager export format: *_DD_MM_YYYY_HH-MM.json
        license: License information for the cleaned dataset (optional, added to metadata)

    Returns:
        Tuple of (cleaned_machines_list, output_filepath)

    Raises:
        ValueError: If create_linked_data=True but base_domain is not provided

    Example:
        >>> machines, filepath = clean_machines_data(
        ...     input_file='exports/machines_raw.json',
        ...     output_file='exports/machines_cleaned.json',
        ...     include_disabled=False,
        ...     create_linked_data=True,
        ...     base_domain='https://example-fabmanager.com',
        ...     updated_at_mode='only_date',
        ...     created_at_mode='only_date'
        ... )
        >>> print(f"Cleaned {len(machines)} machines, saved to {filepath}")

    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If input file is not valid JSON
        ValueError: If create_linked_data=True but base_domain is not provided
    """
    # Validate parameters
    if create_linked_data and not base_domain:
        raise ValueError(
            "base_domain is required when create_linked_data=True. "
            "Please provide the base URL of your FabManager instance "
            "(e.g., base_domain='https://example-fabmanager.com')"
        )

    # Read input file
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Extract timestamp from filename if data_exported_at not provided
    if data_exported_at is None:
        data_exported_at = extract_timestamp_from_filename(input_path.name)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract machines array
    if isinstance(data, dict) and "machines" in data:
        machines = data["machines"]
    elif isinstance(data, list):
        machines = data
    else:
        raise ValueError(
            "Input file must contain a 'machines' key or be a list of machines"
        )

    # Clean each machine
    cleaned_machines = []
    for machine in machines:
        cleaned = clean_machine_record(
            machine=machine,
            include_disabled=include_disabled,
            create_linked_data=create_linked_data,
            base_domain=base_domain,
            updated_at_mode=updated_at_mode,
            created_at_mode=created_at_mode,
        )
        if cleaned is not None:  # None means filtered out
            cleaned_machines.append(cleaned)

    # Generate output filename if not provided
    output_path: Union[str, Path]
    if output_file is None:
        timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M")
        suffix = "linked" if create_linked_data else "cleaned"
        output_path = (
            input_path.parent / f"FabManager_Machines_Cleaned_{suffix}_{timestamp}.json"
        )
    else:
        output_path = Path(output_file)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Build metadata - only include fields that are provided
    metadata = {
        "data_cleaned_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }

    # Add optional metadata fields if provided
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

    # Save cleaned data
    output_data = {"machines": cleaned_machines, "metadata": metadata}

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return cleaned_machines, str(output_path)


__all__ = [
    "clean_machines_data",
    "clean_machine_record",
    "clean_html_keep_links",
    "process_timestamp_field",
    "create_linked_data_uri",
]
