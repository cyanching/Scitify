#!/usr/bin/env python3

# This function of Scitify is used to grep bioRxiv entries matching keyword criteria, 
# the keywords can be modified in /Scitify/config/bioRxiv_keywords.txt
# The number of past days for update searching as well as the batch size of papers 
# (return up to this number of papers for each search) can be specified as the following:
# python3 bioRxiv_retrieve.py --days_before_today 10 --batch_size 200

# Copyright 2024, Cyan Ching, a PhD student at The Physical Chemistry Curie Lab of Institut Curie in France
# This code is up to date as of October 2024.

import requests
import json
import configparser
import argparse
from datetime import datetime, timedelta
import os
import sys

def print_header():
    header = r"""
     ______                _            
    \  ___)              | |           
     \ \__   ___ ___ _  _| |_  _  _  _ 
      > > \ / / (   ) |/     \| || || |
     / /_\ v /| || || ( (| |) ) \| |/ |
    /_____> <  \_)\_)\_)_   _/ \_   _/ 
         / ^ \           | |     | |   
        /_/ \_\          |_|     |_|   
    
    Welcome to Scitify - Your Custom New Scientific Publication Notifier!
    
    Author: Cyan Ching, PhD Student at Institut Curie
    Version: 1.0 | Date: October 2024
    
    """
    print(header)

if __name__ == "__main__":
    print_header()

# Load keywords from the text file
def load_keywords_from_file(file_path):
    config = configparser.ConfigParser(allow_no_value=True)
    
    if not os.path.exists(file_path):
        return None  # Return None if the file doesn't exist
    
    config.read(file_path)

    keywords = {
        "keywords": [],
        "exclude_keywords": [],
        "required_keywords": []
    }

    if "keywords" in config:
        keywords["keywords"] = list(config["keywords"].keys())

    if "exclude_keywords" in config:
        keywords["exclude_keywords"] = list(config["exclude_keywords"].keys())

    if "required_keywords" in config:
        keywords["required_keywords"] = list(config["required_keywords"].keys())

    return keywords

# Define the command-line arguments and --help flag
parser = argparse.ArgumentParser(
    description=(
        "This function of Scitify searches bioRxiv for papers matching keywords.\n"
        "Both flags --days_before_today and --batch_size are required.\n"
        "The keywords should be defined in '/Scitify/config/bioRxiv_keywords.txt'.\n\n"
        "Example usage:\n"
        "  python3 bioRxiv_retrieve.py --days_before_today 10 --batch_size 200\n\n"
        "Created by Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France.\n"
        "This code is up-to-date as of October 2024."
    ),
    formatter_class=argparse.RawTextHelpFormatter,
    add_help=False  # Disable automatic help flag so we can handle it manually
)

# Define optional arguments
parser.add_argument('--days_before_today', type=int, help='Number of days before today to search for papers.')
parser.add_argument('--batch_size', type=int, help='Number of entries to fetch per batch.')
parser.add_argument('--quiet', action='store_true', help='Suppress output of retrieved and excluded lines.')
parser.add_argument('--help', action='store_true', help='Show this help message and exit.')

# Parse command-line arguments
args = parser.parse_args()

# Check if help flag is used
if args.help:
    parser.print_help()
    sys.exit(0)

# Perform manual validation for required flags
errors = []

if args.days_before_today is None:
    errors.append("Error: --days_before_today flag is required.")
if args.batch_size is None:
    errors.append("Error: --batch_size flag is required.")

# Check the keyword file and load it
keywords_file = "../config/bioRxiv_keywords.txt"
keywords_dict = load_keywords_from_file(keywords_file)

# Check for missing or empty keyword file
if keywords_dict is None:
    errors.append(f"Error: The keyword file '{keywords_file}' does not exist. Please ensure the file is present.")
elif not keywords_dict["keywords"]:
    errors.append(f"Error: No keywords found in '{keywords_file}'. Please specify at least one keyword.")

# If there are any errors, print them and exit
if errors:
    for error in errors:
        print(error)
    sys.exit(1)

# Define search parameters
keywords = keywords_dict["keywords"]
exclude_keywords = keywords_dict["exclude_keywords"]
required_keywords = keywords_dict["required_keywords"]

start_date = (datetime.now() - timedelta(days=args.days_before_today)).strftime('%Y-%m-%d')
end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

entries = []

# Iterate over keywords to search separately
for keyword in keywords:
    offset = 0  # Reset offset for each keyword

    while True:
        search_url = f"https://api.biorxiv.org/details/biorxiv/{start_date}/{end_date}/{offset}"

        # Send the search request
        response = requests.get(search_url)
        response_data = response.json()

        # Check if data is available
        if response.status_code == 200 and "collection" in response_data:
            collection = response_data["collection"]
            if not collection:
                break  # No more entries to fetch

            # Iterate through each item in the collection
            for item in collection:
                abstract = item.get("abstract", "").lower()
                combined_text = (item['title'] + " " + item['abstract']).lower()

                # Check if any keyword is present in the abstract
                if keyword.lower() in abstract:
                    # Check for exclude keywords
                    if exclude_keywords and any(exclude_keyword.lower() in combined_text for exclude_keyword in exclude_keywords):
                        if not args.quiet:
                            print(f"Excluded (excluded keyword): {item['title']}")
                        continue

                    # Check for required keywords
                    if required_keywords:
                        score = sum(req_keyword.lower() in combined_text for req_keyword in required_keywords)
                        if score == 0:
                            if not args.quiet:
                                print(f"Excluded (missing required keyword): {item['title']}")
                            continue

                    # Properly handle the authors list
                    authors_list = item.get('authors', [])
                    if isinstance(authors_list, list):
                        authors = ', '.join(authors_list)
                    else:
                        authors = authors_list  # Fallback if it's not a list

                    # Create the entry
                    entry = (
                        f"Title: {item['title']}\n"
                        f"Authors: {authors}\n"
                        f"Date: {item['date']}\n"
                        f"DOI: {item['doi']}\n"
                        f"URL: https://doi.org/{item['doi']}\n"
                        f"Abstract: {item['abstract']}\n\n"
                    )
                    entries.append(entry)

                    # Only print if not in quiet mode
                    if not args.quiet:
                        print(f"Retrieved: {item['title']}")

            # Update the offset to get the next batch
            offset += args.batch_size
        else:
            print("Failed to retrieve data from bioRxiv. Please try again later.")
            break

# Write the entries to a text file
if entries:
    with open("../output/latest_bioRxiv_entries.txt", "w") as file:
        file.writelines(entries)
    print(f"{len(entries)} entries successfully written to '/Scitify/output/latest_bioRxiv_entries.txt'.")
else:
    print("No matching entries found for the given keywords.")



