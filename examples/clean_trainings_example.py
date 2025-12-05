#!/usr/bin/env python3
"""
Example: Clean training data from FabManager export.

This example demonstrates how to use the clean_trainings_data function
to clean and prepare training data for Open Data publishing.
"""

from fabmanager_data_analyzer_zumat import clean_trainings_data

trainings, output_path = clean_trainings_data(
    input_file="fabmanager_trainings_export.json",
    include_disabled=False,
    create_linked_data=True,
        base_domain="YourFabManagerDomain.com/trainings",
    updated_at_mode='remove', # Options: 'remove', 'only_date', 'full_timestamp'
    created_at_mode='remove', # Options: 'remove', 'only_date', 'full_timestamp'
    include_nb_total_places=True, # Include the total places field
    data_owner='Your name or organization',
    data_steward='Your name or organization',
    data_curator='Your name or organization',
    data_exported_from='FabManager instance at YourFabManagerDomain.com',
    license='Your chosen license'
)

print(60*"-")
print(f"✓ Cleaned {len(trainings)} trainings")
print(f"✓ Output saved to: {output_path}")
print(60*"-")