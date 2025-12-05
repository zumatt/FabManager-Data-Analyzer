# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Extract accounting data
- Extract bookable machines data
- Extract events data
- Extract invoices data
- Extract plan categories data
- Extract plans data
- Extract prices data
- Extract spaces data
- Extract subscriptions data
- Extract user trainings data
- Data analysis features for reservations vs trainings comparison


## [0.1.0] - 2025-12-02

### Added
- Initial package structure setup
- Project configuration (pyproject.toml)
- Basic project scaffolding


## [0.2.0] - 2025-12-05

### Added

#### Core Modules
- `api_client.py`: API client for FabManager Open API communication
- `utils.py`: Utility functions for data processing

#### Data Extraction Modules
- `extract_machines.py`: Extract machines data from FabManager API
- `extract_reservations.py`: Extract reservations data with divide-by-type option
- `extract_trainings.py`: Extract trainings data from FabManager API
- `extract_users.py`: Extract users data from FabManager API

#### Data Cleaning Modules
- `clean_machines_data.py`: Filter disabled machines, create linked data URIs, clean HTML content
- `clean_reservations_machine.py`: Anonymize and export machine reservations as Open Data and Linked Open Data (JSON-LD)
- `clean_reservations_training.py`: Anonymize and export training reservations as Open Data and Linked Open Data (JSON-LD)
- `clean_trainings_data.py`: Clean and process trainings data
- `merge_cleaned_data.py`: Merge cleaned datasets

#### Examples
- Complete examples for all extraction and cleaning operations
- Machine data extraction and cleaning examples
- Reservation data extraction and cleaning examples (machine and training types)
- Training data extraction and cleaning examples
- User data extraction examples
- Data merging examples

#### Package Configuration
- Package metadata and PyPI-ready configuration
- Development dependencies (pytest, pytest-cov, black, flake8, mypy, isort)
- Production dependencies (requests>=2.31.0)
- Python 3.8+ support
- Comprehensive README with feature documentation
- Contributing guidelines
- Citation file (CFF format)
- GNU Affero General Public License v3

### Features
- Export data anonymized as Open Data in JSON format
- Export data pseudo-anonymized as Linked Open Data in JSON-LD format
- Support for both anonymized and pseudo-anonymized data exports
- HTML content cleaning for machine descriptions
- Linked data URI generation for resources