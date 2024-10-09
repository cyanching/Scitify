#!/usr/bin/env python3

# This Scitify function is used to tweet each title and URL from a sequential text file ('/Scitify/output/titles_and_urls.txt') using the Twitter API.
# Usage examples:
#   python3 twitter_papers.py --credentials_key twitter_credentials
#
# Note: The '/Scitify/output/titles_and_urls.txt' file must exist, and a valid credentials key must be provided for tweeting.
# Credentials should be stored using the 'keyring' library.
#
# Copyright (C) 2024 Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France.
# This code is up to date as of October 2024.

import tweepy
import keyring
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

# Helper function to check for missing flags or file
def check_errors(args, file_path):
    error_messages = []

    # Check if the credentials key is provided
    if not args.credentials_key:
        error_messages.append("Error: --credentials_key flag is required.")

    # Check if the file exists
    if not os.path.exists(file_path):
        error_messages.append(f"Error: The file '{file_path}' does not exist.")

    # If there are errors, print them and exit
    if error_messages:
        for error in error_messages:
            print(error)
        sys.exit(1)

# Custom function to display the help message
def print_help():
    help_message = """usage: twitter_papers.py [--help] --credentials_key CREDENTIALS_KEY

This Scitify function is used to tweet each title and URL from a sequential text file ('/Scitify/output/titles_and_urls.txt') using the Twitter API.

Example usage:
  python3 twitter_papers.py --credentials_key twitter_credentials

Note: The '/Scitify/output/titles_and_urls.txt' file must exist, and a valid credentials key must be provided for tweeting.

Created by: Cyan Ching, PhD student at The Physical Chemistry Curie Lab, Institut Curie, France.
Date: October 2024
"""
    print(help_message)
    sys.exit()

# Initialize argument parser without default help
parser = argparse.ArgumentParser(add_help=False)

# Add custom --help flag
parser.add_argument('--help', action='store_true', help="Show this help message and exit.")
parser.add_argument('--credentials_key', required=False, help="Specify the credentials key stored in the keyring.")

# Parse arguments
args = parser.parse_args()

# Display custom help if --help is provided
if args.help:
    print_help()

# File path to the 'titles_and_urls.txt'
file_path = '../output/titles_and_urls.txt'

# Check for errors in parallel (missing credentials key or missing file)
check_errors(args, file_path)

# Retrieve Twitter credentials from keyring
bearer_token = keyring.get_password(args.credentials_key, "bearer_token")
api_key = keyring.get_password(args.credentials_key, "api_key")
api_key_secret = keyring.get_password(args.credentials_key, "api_key_secret")
access_token = keyring.get_password(args.credentials_key, "access_token")
access_token_secret = keyring.get_password(args.credentials_key, "access_token_secret")

# Ensure all credentials are available
if not all([bearer_token, api_key, api_key_secret, access_token, access_token_secret]):
    print(f"Error: One or more credentials are missing for the key '{args.credentials_key}'.")
    sys.exit(1)

# Initialize the Client (v2) using credentials from keyring
client = tweepy.Client(bearer_token, api_key, api_key_secret, access_token, access_token_secret)

# Open the 'titles_and_urls.txt' file and read each pair of title and URL
with open(file_path, 'r') as file:
    lines = [line.strip() for line in file if line.strip()]  # Remove empty lines and whitespace

# Post each title and URL sequentially as a tweet
for i in range(0, len(lines), 2):  # Iterate two lines at a time (title + URL)
    if i + 1 < len(lines):  # Ensure there is a URL after the title
        title = lines[i]  # Take the title
        url = lines[i + 1]  # Take the corresponding URL
        tweet = f"{title}\n{url}"  # Combine title and URL into one tweet
        try:
            client.create_tweet(text=tweet)
            print(f'Successfully tweeted: {tweet}')
        except tweepy.errors.TweepyException as e:
            print(f'Failed to tweet: {tweet}, due to: {e}')
    else:
        print(f"Warning: No URL found for the title: {lines[i]}")



