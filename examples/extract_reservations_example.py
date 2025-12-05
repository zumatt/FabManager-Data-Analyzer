#!/usr/bin/env python3
"""
Example script for extracting reservation data from FabManager

This script demonstrates how to use the fabmanager_data_analyzer_zumat package
to extract reservation data from a FabManager instance.
"""

from fabmanager_data_analyzer_zumat import extract_and_save_reservations

reservations, filepath = extract_and_save_reservations(
    base_url="https://your_fabmanager_domain.com",
    api_token="your_token_here",
    output_path='exports/',
    #per_page=100, # Number of records per page (adjust as needed)
    #max_pages=10, # Maximum number of pages to fetch (adjust as needed)
    #add_timestamp= True, # Set to True to add a timestamp to the output file name
    divide_by_type=False, # Set to True to create separate files for each type
    #show_progress=True # Set to True to display a progress bar
)

print(60*"-")
print(f"✓ Extracted {len(reservations)} reservations")
print(f"✓ Data saved to: {filepath}")
print(60*"-")