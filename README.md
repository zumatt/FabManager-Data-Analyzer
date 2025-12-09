# FabManager Data Analyzer

[![DOI](https://zenodo.org/badge/1108603832.svg)](https://doi.org/10.5281/zenodo.17830281)

A Python package for extracting, anonymizing, and analyzing data from FabManager using the Open API.

## Overview

The project has started as a collection of Python notebooks for reading data from FabManager using APIs. The current version is being developed as a comprehensive package to perform data extraction, anonymization, and analysis tasks.

## Features

### Data Extraction from FabManager
- ✅ Extract machines data
- ✅ Extract reservations data (with divide-by-type option)
- ✅ Extract trainings data
- ✅ Extract users data

**Additional extractions** (contributions welcome):
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

### Data Export for Open Data Publishing
Export and clean data from FabManager for publication as [Open Data](https://en.wikipedia.org/wiki/Open_data):
- ✅ Clean machine data (filter disabled, create linked data URIs, clean HTML)
- ✅ Clean reservations data (machine and training reservations)
- ✅ Clean trainings data
- ✅ Merge cleaned datasets

### Data Analysis
**Analysis features** (contributions welcome):
- Analyze reservations in comparison with trainings data

## Installation

### Requirements
- Python >= 3.8
- requests >= 2.31.0

### Install from GitHub

It is suggested to create a virtual environment to install the package by doing the following:

**On macOS/Linux:**
```bash
mkdir testFabManagerExport && cd testFabManagerExport && python -m venv venv
source venv/bin/activate
pip install git+https://github.com/zumatt/FabManager-Data-Analyzer.git
```

**On Windows:**
```bash
mkdir testFabManagerExport
cd testFabManagerExport
python -m venv venv
venv\Scripts\activate
pip install git+https://github.com/zumatt/FabManager-Data-Analyzer.git
```

To use the installed package you can easily select an example and execute it.

### Install for development

Clone the repository and install in editable mode:

```bash
git clone https://github.com/zumatt/FabManager-Data-Analyzer.git
cd FabManager-Data-Analyzer
pip install -e ".[dev]"
```

This installs the package in editable mode along with development dependencies including:
- pytest (testing framework)
- pytest-cov (code coverage)
- black (code formatter)
- flake8 (linter)
- mypy (type checker)
- isort (import sorter)

## Usage

For usage examples, please refer to the [`examples/`](examples/) directory, which contains:
- `extract_machines_example.py` - Extract machines data from FabManager
- `extract_reservations_example.py` - Extract reservations data
- `extract_trainings_example.py` - Extract trainings data
- `extract_users_example.py` - Extract users data
- `clean_machines_example.py` - Clean and prepare machine data for Open Data publishing
- `clean_reservations_machine_example.py` - Clean machine reservations data
- `clean_reservations_training_example.py` - Clean training reservations data
- `clean_trainings_example.py` - Clean trainings data
- `merge_cleaned_data_example.py` - Merge cleaned datasets

## Development

### Development Commands

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/

# For testing examples can be used
```

### Troubleshooting

**Import Errors**: Make sure you've installed the package with `pip install -e .`

**Development Tools Not Working**: Install development dependencies manually:
```bash
pip install black flake8 mypy isort pytest pytest-cov
```

## Project Structure

```
FabManager-Data-Analyzer/
├── src/
│   └── fabmanager_data_analyzer_zumat/
│       ├── __init__.py
│       ├── api_client.py
│       ├── utils.py
│       ├── extract_machines.py
│       ├── extract_reservation.py
│       ├── extract_trainings.py
│       ├── extract_users.py
│       ├── clean_machines_data.py
│       ├── clean_reservations_machine.py
│       ├── clean_reservations_training.py
│       ├── clean_trainings_data.py
│       └── merge_cleaned_data.py
├── tests/
├── examples/
│   ├── extract_machines_example.py
│   ├── extract_reservations_example.py
│   ├── extract_trainings_example.py
│   ├── extract_users_example.py
│   ├── clean_machines_example.py
│   ├── clean_reservations_machine_example.py
│   ├── clean_reservations_training_example.py
│   ├── clean_trainings_example.py
│   └── merge_cleaned_data_example.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Documentation

- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)
- [Citation](citation.cff)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the terms specified in the [LICENSE](LICENSE) file.

## Citation

If you use this package in your research, please cite it using the information provided in [citation.cff](citation.cff).

## Related Projects

- [FabManager-Scraping](https://github.com/zumatt/FabManager-Scraping) - The original notebook collection that inspired this package

## Aknowledgements

This package has been developed with the assistance of `Claude Sonnet 4.5`. As a result, you may encounter some unusual behaviors or code repetitions. Contributions to improve code clarity and reduce redundancy are greatly appreciated.