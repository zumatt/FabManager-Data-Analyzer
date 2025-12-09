#!/usr/bin/env python3
"""
Example script for extracting training data from FabManager

This script demonstrates how to use the fabmanager_data_analyzer_zumat package
to extract training data from a FabManager instance.
"""

from fabmanager_data_analyzer_zumat import clean_machines_data

machines, output_path = clean_machines_data(
    input_file="your_fabmanager_exported_file.json",
    #output_file='your_cleaned_machines_data.json', # Optional: specify output file name
    include_disabled=False, 
    create_linked_data=True,
        base_domain="YourFabManagerDomain.com/machines", # Required if create_linked_data is True
    updated_at_mode='remove', # Options: 'remove', 'only_date', 'full_timestamp'
    created_at_mode='remove', # Options: 'remove', 'only_date', 'full_timestamp'
    data_owner='Your name or organization',
    data_steward='Your name or organization',
    data_curator='Your name or organization',
    data_exported_from='FabManager instance at YourFabManagerDomain.com',
    license='Your chosen license',
    timezone='UTC',
)

print(60*"-")
print(f"✓ Cleaned {len(machines)} machines")
print(f"✓ Output saved to: {output_path}")
print(60*"-")