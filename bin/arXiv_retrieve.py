#!/usr/bin/env python3

# This function of Scitify is used to grep arXiv entries matching keyword criteria, 
# the keywords can be modified in /Scitify/config/arXiv_keywords.txt
# The number of past days for update searching as well as the batch size of papers 
# (return up to this number of papers for each search) can be specified as the following:
# python3 arXiv_retrieve.py --days_before_today 10 --batch_size 100

# Copyright 2024, Cyan Ching, a PhD student at The Physical Chemistry Curie Lab of Institut Curie in France
# This code is up to date as of October 2024.

import feedparser
from datetime import datetime, timedelta
import urllib.parse
import configparser
import argparse
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
        "This function of Scitify searches arXiv for papers matching keywords.\n"
        "Both flags --days_before_today and --batch_size are required.\n"
        "The keywords should be defined in '/Scitify/config/arXiv_keywords.txt'.\n\n"
        "Example usage:\n"
        "  python3 arXiv_retrieve.py --days_before_today 10 --batch_size 100\n\n"
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
keywords_file = "../config/arXiv_keywords.txt"
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

entries = {}
processed_links = set()  # To keep track of processed entries

# Iterate over keywords to search separately and use specific fields
for keyword in keywords:
    offset = 0  # Reset offset for each keyword
    while True:
        encoded_keyword = urllib.parse.quote(keyword)
        search_url = f"http://export.arxiv.org/api/query?search_query=abs:{encoded_keyword}&start={offset}&max_results={args.batch_size}&sortBy=submittedDate&sortOrder=descending"

        # Parse the feed
        response = feedparser.parse(search_url)

        # Break if no more entries are returned
        if not response.entries:
            break

        # Iterate through each entry in the response
        for entry in response.entries:
            # Only print if not in quiet mode
            if not args.quiet:
                print(f"Retrieved: {entry.title}")

            # Avoid processing duplicate entries
            if entry.link in processed_links:
                continue

            processed_links.add(entry.link)

            # Convert the published date to match the format and filter by date range
            published_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
            if published_date >= datetime.now() - timedelta(days=args.days_before_today):
                # Check for exclusion keywords in both title and summary without word boundaries
                combined_text = (entry.title + " " + entry.summary).lower()
                if not any(exclude_keyword.lower() in combined_text for exclude_keyword in exclude_keywords):
                    # Apply a scoring mechanism instead of strict matching
                    score = sum(req_keyword.lower() in combined_text for req_keyword in required_keywords)
                    if not required_keywords or score > 0:
                        # Strip whitespace and replace any newline characters in the title
                        clean_title = ' '.join(entry.title.strip().replace('\n', ' ').split())
                        # Use the URL as a unique identifier for entries to avoid duplicates
                        entry_data = (
                            f"Title: {clean_title}\n"
                            f"Authors: {', '.join(author.name for author in entry.authors)}\n"
                            f"Date: {published_date.strftime('%Y-%m-%d')}\n"
                            f"URL: {entry.link}\n"
                            f"Abstract: {entry.summary}\n\n"
                        )
                        entries[entry.link] = entry_data
                    else:
                        if not args.quiet:
                            print(f"Excluded (low score): {entry.title}")
                else:
                    if not args.quiet:
                        print(f"Excluded (excluded keyword): {entry.title}")

        # Update offset for the next batch
        offset += args.batch_size

# Write the unique entries to a text file
if entries:
    with open("../output/latest_arxiv_entries.txt", "w") as file:
        file.writelines(entries.values())
    print(f"{len(entries)} unique entries successfully written to '/Scitify/output/latest_arxiv_entries.txt'.")
else:
    print("No matching entries found for the given keywords.")





