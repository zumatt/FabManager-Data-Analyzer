#!/usr/bin/env python3
"""
Example of merging cleaned FabManager data from multiple sources.

This example demonstrates how to use the merge_cleaned_data function to combine
cleaned machines, trainings, and reservation data into a single unified dataset.
"""

from fabmanager_data_analyzer_zumat import merge_cleaned_data

merged_data, output_path = merge_cleaned_data(
    machines_data_path="your_cleaned_machines_data.json",
    trainings_data_path="your_cleaned_trainings_data.json",
    reservations_machine_data_path="your_cleaned_reservations_machine_data.json",
    reservations_training_data_path="your_cleaned_reservations_training_data.json",
    #output_file='merged_fabmanager_data.json'  # Optional: specify output file name
    #data_owner='Your name or organization', # Optional: specify data owner, in case not specified taken from the first file
    #data_steward='Your name or organization', # Optional: specify data steward, in case not specified taken from the first file
    #data_curator='Your name or organization', # Optional: specify data curator, in case not specified taken from the first file
    #data_exported_from='FabManager instance at YourFabManagerDomain.com', # Optional: specify data exported from, in case not specified taken from the first file
    #license='Your chosen license', # Optional: specify license, in case not specified taken from the first file
    #timezone='UTC', # Optional: specify timezone, in case not specified taken from the first file
)

print(60*"-")
print(f"✓ Merged data contains {len(merged_data['machines'])} machines")
print(f"✓ Merged data contains {len(merged_data['trainings'])} trainings")
print(f"✓ Merged data contains {len(merged_data['reservations_machine'])} machine reservations")
print(f"✓ Merged data contains {len(merged_data['reservations_training'])} training reservations")
print(f"✓ Merged data saved to: {output_path}")
print(60*"-")