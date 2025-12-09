#!/usr/bin/env python3
"""
Example of cleaning machine reservation data from FabManager.

This example demonstrates how to use the clean_reservations_machine_data function
to transform raw reservation exports into cleaned data suitable for analysis or
publication as Open Data.
"""

from fabmanager_data_analyzer_zumat import clean_reservations_machine_data

reservations, output_path = clean_reservations_machine_data(
    input_file="your_fabmanager_machine_reservations_export.json",
    #output_file='cleaned_machine_reservations.json', # Optional: specify output file name
    updated_at_mode='remove', # Options: 'remove', 'only_date', 'full_timestamp'
    created_at_mode='remove', # Options: 'remove', 'only_date', 'full_timestamp'
    create_linked_data=True,
        base_domain='YourFabManagerDomain.com/machines', # Required if create_linked_data is True
    data_owner='Your name or organization',
    data_steward='Your name or organization',
    data_curator='Your name or organization',
    data_exported_from='FabManager instance at YourFabManagerDomain.com',
    license='Your chosen license',
    timezone='UTC',
)

print(60*"-")
print(f"✓ Cleaned {len(reservations)} machine reservations")
print(f"✓ Output saved to: {output_path}")
print(60*"-")