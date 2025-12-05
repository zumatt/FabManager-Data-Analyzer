"""
FabManager Data Analyzer - A Python package for FabManager data extraction and analysis.

This package provides tools to:
- Extract data from FabManager Open API (users, machines, reservations, trainings)
- Anonymize and pseudo-anonymize reservation data
- Export data to JSON
- Analyze FabManager data

Main components:
- API client for FabManager Open API
- Data extraction modules
- Data anonymization modules
- Data export utilities
"""

__version__ = "0.1.0"
__author__ = "Matteo Subet"
__email__ = "matteo.subet@supsi.ch"

# Import main components
from .api_client import FabManagerAPIClient
from .clean_machines_data import clean_html_keep_links as clean_html_keep_links_machines
from .clean_machines_data import (
    clean_machine_record,
    clean_machines_data,
)
from .clean_machines_data import (
    extract_timestamp_from_filename as extract_timestamp_from_filename_machines,
)
from .clean_reservations_machine import (
    calculate_time_spent,
)
from .clean_reservations_machine import (
    clean_reservation_record as clean_machine_reservation_record,
)
from .clean_reservations_machine import (
    clean_reservations_machine_data,
)
from .clean_reservations_training import (
    clean_reservation_record as clean_training_reservation_record,
)
from .clean_reservations_training import (
    clean_reservations_training_data,
)
from .clean_trainings_data import (
    clean_html_keep_links as clean_html_keep_links_trainings,
)
from .clean_trainings_data import (
    clean_training_record,
    clean_trainings_data,
)
from .clean_trainings_data import (
    extract_timestamp_from_filename as extract_timestamp_from_filename_trainings,
)
from .extract_machines import (
    extract_and_save_machines,
    extract_machines,
    save_machines,
)
from .extract_reservation import (
    divide_reservations_by_type,
    extract_and_save_reservations,
    extract_reservations,
    save_reservations,
)
from .extract_trainings import (
    extract_and_save_trainings,
    extract_trainings,
    save_trainings,
)
from .extract_users import (
    extract_and_save_users,
    extract_users,
    save_users,
)
from .merge_cleaned_data import merge_cleaned_data
from .utils import clean_data_for_json, sanitize_filename

# Backward compatibility - provide non-aliased versions defaulting to machines
clean_html_keep_links = clean_html_keep_links_machines
extract_timestamp_from_filename = extract_timestamp_from_filename_machines

# Package metadata
__all__ = [
    "__version__",
    "__author__",
    "__email__",
    # API Client
    "FabManagerAPIClient",
    # Machines
    "extract_machines",
    "save_machines",
    "extract_and_save_machines",
    # Reservations
    "extract_reservations",
    "save_reservations",
    "extract_and_save_reservations",
    "divide_reservations_by_type",
    # Trainings
    "extract_trainings",
    "save_trainings",
    "extract_and_save_trainings",
    # Users
    "extract_users",
    "save_users",
    "extract_and_save_users",
    # Data Cleaning - Machines
    "clean_machines_data",
    "clean_machine_record",
    "clean_html_keep_links_machines",
    "extract_timestamp_from_filename_machines",
    # Data Cleaning - Trainings
    "clean_trainings_data",
    "clean_training_record",
    "clean_html_keep_links_trainings",
    "extract_timestamp_from_filename_trainings",
    # Data Cleaning - Reservations (Machine)
    "clean_reservations_machine_data",
    "clean_machine_reservation_record",
    "calculate_time_spent",
    # Data Cleaning - Reservations (Training)
    "clean_reservations_training_data",
    "clean_training_reservation_record",
    # Data Merging
    "merge_cleaned_data",
    # Backward compatibility (default to machines)
    "clean_html_keep_links",
    "extract_timestamp_from_filename",
    # Utils
    "clean_data_for_json",
    "sanitize_filename",
]
