#!/usr/bin/env python3

# This function of Scitify is used to grep PubMed entries matching keyword criteria, 
# the keywords can be modified in /Scitify/config/PubMed_keywords.txt.
# The number of past days for update searching as well as the batch size of papers 
# (return up to this number of papers for each search) can be specified as follows:
# python3 PubMed_retrieve.py --days_before_today 10 --batch_size 200 --email your_email

# Created by Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France
# This code is up to date as of October 2024.

import requests
from datetime import datetime, timedelta
from Bio import Entrez
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
        "required_keywords": [],
        "journals_of_interest": []  # Optional
    }

    if "keywords" in config:
        keywords["keywords"] = list(config["keywords"].keys())

    if "exclude_keywords" in config:
        keywords["exclude_keywords"] = list(config["exclude_keywords"].keys())

    if "required_keywords" in config:
        keywords["required_keywords"] = list(config["required_keywords"].keys())

    if "journals_of_interest" in config:
        keywords["journals_of_interest"] = list(config["journals_of_interest"].keys())

    return keywords

# Define the command-line arguments
parser = argparse.ArgumentParser(
    description=(
        "This function of Scitify searches PubMed for papers matching keywords.\n"
        "Both --days_before_today, --batch_size, and --email flags are required.\n"
        "The keywords should be defined in '/Scitify/config/PubMed_keywords.txt'.\n\n"
        "Example usage:\n"
        "  python3 PubMed_retrieve.py --days_before_today 10 --batch_size 200 --email your_email\n\n"
        "Created by Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France.\n"
        "This code is up-to-date as of October 2024."
    ),
    add_help=False,  # Disable automatic -h
    formatter_class=argparse.RawTextHelpFormatter
)

# Define optional arguments
parser.add_argument('--days_before_today', type=int, help='Number of days before today to search for papers.')
parser.add_argument('--batch_size', type=int, help='Number of entries to fetch per batch.')
parser.add_argument('--email', type=str, help='Email to be used for PubMed queries (required).')
parser.add_argument('--quiet', action='store_true', help='Suppress output of retrieved and excluded lines.')
parser.add_argument('--help', action='help', help='Show this help message and exit.')

# Parse command-line arguments
args = parser.parse_args()

# Manual check for required arguments
errors = []

# Add checks for missing required arguments
if args.days_before_today is None:
    errors.append("Error: --days_before_today flag is required.")
if args.batch_size is None:
    errors.append("Error: --batch_size flag is required.")
if args.email is None:
    errors.append("Error: --email flag is required.")

# Check the keyword file and load it
keywords_file = "../config/PubMed_keywords.txt"
keywords_dict = load_keywords_from_file(keywords_file)

# Check for missing or empty keyword file
if keywords_dict is None:
    errors.append(f"Error: The keyword file '{keywords_file}' does not exist. Please ensure the file is present.")
elif not keywords_dict["keywords"]:
    errors.append(f"Error: No keywords found in '{keywords_file}'. Please specify at least one keyword.")

# If there are any errors, print them and exit
if errors:
    sys.stderr.write("\n".join(errors) + "\n")
    sys.exit(1)

# Assign command-line arguments to variables
days_before_today = args.days_before_today
batch_size = args.batch_size
Entrez.email = args.email

# Define search parameters
keywords = keywords_dict["keywords"]
exclude_keywords = keywords_dict["exclude_keywords"]
required_keywords = keywords_dict["required_keywords"]
journals_of_interest = keywords_dict["journals_of_interest"]

start_date = (datetime.now() - timedelta(days=days_before_today)).strftime('%Y/%m/%d')
end_date = datetime.now().strftime('%Y/%m/%d')  # Include today in the end date

# Month mapping for converting text month names to numbers
month_mapping = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"
}

entries = []

# Search each keyword individually
for keyword in keywords:
    retstart = 0

    # Construct PubMed query for the current keyword
    query = f"({keyword})"
    
    # Only include the journal filter if journals of interest are specified
    if journals_of_interest:
        query += f" AND ({' OR '.join([f'{journal}[Journal]' for journal in journals_of_interest])})"
    
    if exclude_keywords:
        query += " NOT " + " NOT ".join(exclude_keywords)  # Exclude specific keywords if any

    # Use Entrez to search PubMed and paginate
    while True:
        try:
            search_handle = Entrez.esearch(db="pubmed", term=query, datetype="pdat", mindate=start_date, maxdate=end_date, retmax=batch_size, retstart=retstart)
            search_results = Entrez.read(search_handle)
            search_handle.close()
        except Exception as e:
            print(f"Error querying PubMed: {e}")
            break

        # Extract IDs and fetch details
        pubmed_ids = search_results['IdList']
        if not pubmed_ids:
            break

        try:
            fetch_handle = Entrez.efetch(db="pubmed", id=pubmed_ids, rettype="medline", retmode="xml")
            fetch_results = Entrez.read(fetch_handle)
            fetch_handle.close()
        except Exception as e:
            print(f"Error fetching PubMed entries: {e}")
            break

        # Iterate through each retrieved paper
        for article in fetch_results['PubmedArticle']:
            article_info = article['MedlineCitation']['Article']
            journal = article_info['Journal']['Title'].lower()

            # If journals of interest are specified, filter by journal
            if not journals_of_interest or any(journal_name.lower() in journal for journal_name in journals_of_interest):
                title = article_info.get('ArticleTitle', 'No Title')
                authors = ", ".join(
                    [
                        f"{author['LastName']} {author.get('Initials', '')}"
                        for author in article_info.get('AuthorList', [])
                        if 'LastName' in author
                    ]
                )
                pub_date = article_info['Journal']['JournalIssue']['PubDate']

                # Construct the full date if available (year, month, day)
                year = pub_date.get('Year', 'No Year')
                month = pub_date.get('Month', '').lower()[:3]  # Convert to lowercase and get the first three letters
                day = pub_date.get('Day', '')

                # Convert the month name to a numeric value
                month_num = month_mapping.get(month, "01")  # Default to January if not found

                # Format the date as YYYY-MM-DD
                if year != 'No Year':
                    date_str = f"{year}-{month_num}-{day.zfill(2) if day else '01'}"
                else:
                    date_str = "Unknown Date"

                abstract = article_info.get('Abstract', {}).get('AbstractText', ['No Abstract'])[0]

                # Get DOI or ELocationID to construct full-text link
                elocation_ids = article_info.get('ELocationID', [])
                doi = None
                for eloc in elocation_ids:
                    if eloc.attributes.get('EIdType') == 'doi':
                        doi = eloc
                        break

                # Construct full-text link from DOI if available
                if doi:
                    full_text_url = f"https://doi.org/{doi}"
                else:
                    full_text_url = "Full text link not available"

                # Create entry for each paper
                entry = (
                    f"Title: {title}\n"
                    f"Authors: {authors}\n"
                    f"Journal: {journal.capitalize()}\n"
                    f"Date: {date_str}\n"
                    f"URL: {full_text_url}\n"
                    f"Abstract: {abstract}\n\n"
                )
                entries.append(entry)

                # Only print if not in quiet mode
                if not args.quiet:
                    print(f"Retrieved: {title}")

        # Update retstart for the next batch
        retstart += batch_size

        # If the total results have been fetched, break the loop
        if retstart >= int(search_results['Count']):
            break

# Write the entries to a text file
if entries:
    with open("../output/latest_pubmed_entries.txt", "w") as file:
        file.writelines(entries)
    print(f"{len(entries)} entries successfully written to '/Scitify/output/latest_pubmed_entries.txt'.")
else:
    print("No matching entries found for the given keywords.")






