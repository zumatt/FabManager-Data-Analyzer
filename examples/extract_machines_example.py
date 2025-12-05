#!/usr/bin/env python3
"""
Example script for extracting machine data from FabManager

This script demonstrates how to use the fabmanager_data_analyzer_zumat package
to extract machine data from a FabManager instance.
"""

from fabmanager_data_analyzer_zumat import extract_and_save_machines

# Extract and save machines
machines, filepath = extract_and_save_machines(
    base_url='https://your_fabmanager_domain.com',
    api_token='your_token_here',
    output_path='exports/',
)

print(60*"-")
print(f"✓ Extracted {len(machines)} machines")
print(f"✓ Data saved to: {filepath}")
print(60*"-")