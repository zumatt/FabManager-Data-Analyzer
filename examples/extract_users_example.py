#!/usr/bin/env python3
"""
Example script for extracting user data from FabManager

This script demonstrates how to use the fabmanager_data_analyzer_zumat package
to extract user data from a FabManager instance.
"""

from fabmanager_data_analyzer_zumat import extract_and_save_users

users, filepath = extract_and_save_users(
    base_url="https://your_fabmanager_domain.com",
    api_token="your_token_here",
    output_path='exports/',
    #custom_filename='fabmanager_users.json', # Optional: specify custom output file name
    #show_progress=True # Set to True to display a progress bar
)

print(60*"-")
print(f"✓ Extracted {len(users)} users")
print(f"✓ Data saved to: {filepath}")
print(60*"-")