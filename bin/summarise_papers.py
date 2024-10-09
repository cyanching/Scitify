#!/usr/bin/env python3

# This function of Scitify is used to extract titles and URLs from the latest articles found in arXiv, bioRxiv, and PubMed source files.
# It generates a '/Scitify/output/titles_and_urls.txt' file containing the extracted information.
#
# Usage example:
#   python3 summarise_papers.py
#
# Copyright (C) 2024 Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France.
# This code is up to date as of October 2024.

import os
import argparse
import sys
from datetime import datetime

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
    
    Welcome to Scitify - Your Custom Scientific Paper Retriever!
    
    Author: Cyan Ching, PhD Student at Institut Curie
    Version: 1.0 | Date: October 2024
    
    """
    print(header)

if __name__ == "__main__":
    print_header()

# Custom function to display the help message in the desired format
def print_help():
    help_message = """usage: summarise_papers.py [--help]

This function of Scitify is used to extract titles and URLs from the latest articles found in arXiv, bioRxiv, and PubMed source files.
It generates a '/Scitify/output/titles_and_urls.txt' file containing the extracted information.

Example usage:
  python3 summarise_papers.py

Created by: Cyan Ching, PhD student at The Physical Chemistry Curie Lab, Institut Curie, France.
Date: October 2024
"""
    print(help_message)
    sys.exit()

# Initialize argument parser without default help
parser = argparse.ArgumentParser(add_help=False)

# Add custom --help flag
parser.add_argument('--help', action='store_true', help="Show this help message and exit.")

# Parse arguments
args = parser.parse_args()

# Display custom help if --help is provided
if args.help:
    print_help()

# Define file names
files = ["../output/latest_arxiv_entries.txt", "../output/latest_bioRxiv_entries.txt", "../output/latest_pubmed_entries.txt"]

# Output file name
output_file = "../output/titles_and_urls.txt"

# Helper function to extract information from text files
def extract_entries(file):
    entries = []
    if os.path.exists(file):
        with open(file, "r") as f:
            entry = {}
            for line in f:
                line = line.strip()
                if line.startswith("Title:"):
                    entry["title"] = line[len("Title: "):]
                elif line.startswith("Date:"):
                    try:
                        date_str = line[len("Date: "):]
                        entry["date"] = datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        entry["date"] = None
                elif line.startswith("URL:"):
                    entry["url"] = line[len("URL: "):]
                elif line == "":  # An empty line indicates the end of an entry
                    if "title" in entry and "date" in entry and "url" in entry:
                        entries.append(entry)
                    entry = {}
    return entries

# Extract entries from all files
all_entries = []
for file in files:
    if os.path.exists(file):
        all_entries.extend(extract_entries(file))

# Sort all entries by publication date (newest first)
all_entries = sorted(all_entries, key=lambda x: x["date"], reverse=True)

# Open the output file for writing and collect the content for the file
with open(output_file, "w") as output:
    if all_entries:
        for entry in all_entries:
            title = entry.get("title")
            url = entry.get("url")
            entry_content = f"{title}\n{url}\n\n"
            output.write(entry_content)
    else:
        output.write("No entries found for the given sources.\n")

print(f"Titles and URLs have been successfully written to /Scitify/output/titles_and_urls.txt.")

# Include messages for missing files
for file in files:
    if not os.path.exists(file):
        source_name = os.path.basename(file).split('_')[1]
        print(f"No entries were found for {source_name}.")


