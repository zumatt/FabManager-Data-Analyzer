"""
Clean and transform training data from FabManager exports.

This module provides functions to clean and prepare training data for analysis or publication
as Open Data. It offers various cleaning options including filtering disabled trainings,
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
        >>> extract_timestamp_from_filename('FabManager_ExportedData_Trainings_01_01_2025_00-00.json')
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
        html_content: HTML string to clean

    Returns:
        Cleaned text with links preserved in readable format

    Example:
        >>> clean_html_keep_links('<p>Visit <a href="https://example.com">our site</a></p>')
        'Visit our site (https://example.com)'
    """
    if not html_content:
        return ""

    parser = HTMLLinkExtractor()
    try:
        parser.feed(html_content)
        return str(parser.get_text())
    except Exception:
        # If parsing fails, just strip all tags
        return re.sub(r"<[^>]+>", "", html_content).strip()


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


def create_linked_data_uri(base_domain: str, slug: str) -> str:
    """
    Create a linked data URI from base domain and slug.

    Args:
        base_domain: The base domain (e.g., 'https://example-fabmanager.com')
        slug: The training slug

    Returns:
        Complete URI for the training

    Example:
        >>> create_linked_data_uri('https://example-fabmanager.com', 'basic-training')
        'https://example-fabmanager.com/basic-training'
    """
    # Remove trailing slash from base_domain if present
    base_domain = base_domain.rstrip("/")
    # Remove leading slash from slug if present
    slug = slug.lstrip("/")

    return f"{base_domain}/{slug}"


def clean_training_record(
    training: Dict,
    include_disabled: bool = True,
    create_linked_data: bool = False,
    base_domain: Optional[str] = None,
    updated_at_mode: Literal["all", "only_date", "remove"] = "all",
    created_at_mode: Literal["all", "only_date", "remove"] = "all",
    include_nb_total_places: bool = True,
) -> Optional[Dict]:
    """
    Clean a single training record.

    Args:
        training: Training record to clean
        include_disabled: Whether to include disabled trainings
        create_linked_data: Whether to create linked data URIs
        base_domain: Base domain for linked data (required if create_linked_data=True)
        updated_at_mode: How to handle updated_at field ('all', 'only_date', 'remove')
        created_at_mode: How to handle created_at field ('all', 'only_date', 'remove')
        include_nb_total_places: Whether to include the nb_total_places field

    Returns:
        Cleaned training record or None if filtered out
    """
    # Filter disabled trainings if requested
    if not include_disabled and training.get("disabled") is not None:
        return None

    # Create a copy to avoid modifying the original
    cleaned = training.copy()

    # Remove ID field
    if "id" in cleaned:
        del cleaned["id"]

    # Remove disabled field when filtering (only keep enabled trainings without the field)
    if not include_disabled:
        cleaned.pop("disabled", None)

    # Create linked data URI if requested
    if create_linked_data:
        if not base_domain:
            raise ValueError("base_domain is required when create_linked_data=True")

        slug = cleaned.get("slug")
        if slug:
            cleaned["url"] = create_linked_data_uri(base_domain, slug)

        # Remove slug field when creating linked data
        cleaned.pop("slug", None)

    # Process timestamp fields
    if "updated_at" in cleaned:
        processed = process_timestamp_field(cleaned["updated_at"], updated_at_mode)
        if processed is None:
            cleaned.pop("updated_at", None)
        else:
            cleaned["updated_at"] = processed

    if "created_at" in cleaned:
        processed = process_timestamp_field(cleaned["created_at"], created_at_mode)
        if processed is None:
            cleaned.pop("created_at", None)
        else:
            cleaned["created_at"] = processed

    # Clean HTML in description field
    if "description" in cleaned and cleaned["description"]:
        cleaned["description"] = clean_html_keep_links(cleaned["description"])

    # Handle nb_total_places field
    if not include_nb_total_places:
        cleaned.pop("nb_total_places", None)

    return cleaned


def clean_trainings_data(
    input_file: str,
    output_file: Optional[str] = None,
    include_disabled: bool = True,
    create_linked_data: bool = False,
    base_domain: Optional[str] = None,
    updated_at_mode: Literal["all", "only_date", "remove"] = "all",
    created_at_mode: Literal["all", "only_date", "remove"] = "all",
    include_nb_total_places: bool = True,
    data_owner: Optional[str] = None,
    data_steward: Optional[str] = None,
    data_curator: Optional[str] = None,
    data_exported_from: Optional[str] = None,
    data_exported_at: Optional[str] = None,
    license: Optional[str] = None,
) -> Tuple[List[Dict], str]:
    """
    Clean and transform training data from FabManager export.

    This function reads a FabManager training export file, applies various cleaning
    operations, and saves the result to a new file with optional metadata.

    Args:
        input_file: Path to the input JSON file
        output_file: Path for the output file. If None, generates automatic name
        include_disabled: If True, include all trainings. If False, filter out disabled trainings
                         and remove the 'disabled' field from the output
        create_linked_data: If True, create 'url' field with full URI and remove 'slug' field.
                           Requires base_domain to be provided
        base_domain: Base domain for linked data URIs (e.g., 'https://example-fabmanager.com').
                    Required when create_linked_data=True
        updated_at_mode: How to handle updated_at timestamps:
                        - 'all': Keep full ISO timestamp
                        - 'only_date': Keep only date (YYYY-MM-DD)
                        - 'remove': Remove the field entirely
        created_at_mode: How to handle created_at timestamps (same options as updated_at_mode)
        include_nb_total_places: If True, keep the nb_total_places field. If False, remove it
        data_owner: Organization or person who owns the data (optional, added to metadata)
        data_steward: Person responsible for data quality (optional, added to metadata)
        data_curator: Person who prepared/cleaned the data (optional, added to metadata)
        data_exported_from: URL where data was exported from (optional, added to metadata)
        data_exported_at: Date and time when the original data was exported (optional, added to metadata).
                         If not provided, automatically extracted from input filename if it follows
                         the FabManager export format: *_DD_MM_YYYY_HH-MM.json
        license: License under which the data is published (optional, added to metadata)

    Returns:
        Tuple of (list of cleaned training records, path to output file)

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If create_linked_data=True but base_domain is not provided
        json.JSONDecodeError: If input file is not valid JSON

    Example:
        >>> trainings, path = clean_trainings_data(
        ...     input_file='FabManager_ExportedData_Trainings_01_01_2025_00-00.json',
        ...     output_file='cleaned_trainings.json',
        ...     include_disabled=False,
        ...     create_linked_data=True,
        ...     base_domain='https://example-fabmanager.com',
        ...     updated_at_mode='only_date',
        ...     created_at_mode='only_date',
        ...     include_nb_total_places=True,
        ...     data_owner='Your Organization Name or Person',
        ...     license='License Name'
        ... )
        >>> len(trainings)
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

    # Extract trainings array
    trainings = data.get("trainings", [])

    # Clean each training record
    cleaned_trainings = []
    for training in trainings:
        cleaned = clean_training_record(
            training=training,
            include_disabled=include_disabled,
            create_linked_data=create_linked_data,
            base_domain=base_domain,
            updated_at_mode=updated_at_mode,
            created_at_mode=created_at_mode,
            include_nb_total_places=include_nb_total_places,
        )
        if cleaned is not None:
            cleaned_trainings.append(cleaned)

    # Generate output filename if not provided
    output_path: Union[str, Path]
    if output_file is None:
        timestamp = datetime.now().strftime("%d_%m_%Y_%H-%M")
        suffix = "linked" if create_linked_data else "cleaned"
        output_path = (
            input_path.parent
            / f"FabManager_Trainings_Cleaned_{suffix}_{timestamp}.json"
        )
    else:
        output_path = Path(output_file)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Prepare output data structure
    output_data: Dict = {"trainings": cleaned_trainings}

    # Add metadata if any optional fields are provided
    metadata = {}

    # Add cleaning timestamp
    metadata["data_cleaned_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

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

    if metadata:
        output_data["metadata"] = metadata

    # Write output file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    return cleaned_trainings, str(output_path)
