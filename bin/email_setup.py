#!/usr/bin/env python3

# This function of Scitify is used to securely set up credentials for using either your Outlook or Gmail services for sending paper updates
# Example usages are as the following:
# python3 email_setup.py --email your_email --service outlook_service
# python3 email_setup.py --email your_email --service gmail_service
# Note: If you have two-factor authentication set up, which is common for Gmail, instead of using your general Google password, generate an App Password and use it here instead!

# Copyright (C) 2024 Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France.
# This code is up to date as of October 2024.

import keyring
import argparse
import sys
import getpass

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

# Helper function for parallel error handling
def check_missing_flags(args):
    error_messages = []
    if not args.email:
        error_messages.append("Error: --email flag is required.")
    if not args.service:
        error_messages.append("Error: --service flag is required.")

    if error_messages:
        for error in error_messages:
            print(error)
        sys.exit(1)

# Set up argument parser
description = """
This function of Scitify is used to securely set up credentials for using either your Outlook or Gmail services for sending paper updates.

Example usages:
  python3 email_setup.py --email your_email --service outlook_service
  python3 email_setup.py --email your_email --service gmail_service

Note: If you have two-factor authentication set up (common for Gmail), use an App Password instead of your general account password.

Created by: Cyan Ching, PhD student at The Physical Chemistry Curie Lab, Institut Curie, France.
Date: October 2024
"""

# Initialize the parser with add_help=False and manual --help
parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter, add_help=False)

# Add the custom --help flag
parser.add_argument('--help', action='help', help='Show this help message and exit.')

# Add the command-line arguments
parser.add_argument('--email', required=True, help="The email address to store (e.g., 'your_email@gmail.com').")
parser.add_argument('--service', required=True, choices=['outlook_service', 'gmail_service'],
                    help="The label of the service. Choose either 'outlook_service' or 'gmail_service'.")

# Parse arguments
args = parser.parse_args()

# Check if any flags are missing
check_missing_flags(args)

# Prompt the user for their password securely using getpass
password = getpass.getpass("Enter your email password (input will be hidden): ")

# Store the email address and password securely in the keyring
keyring.set_password(args.service, "email_username", args.email)
keyring.set_password(args.service, "email_password", password)

print("Credentials have been securely stored in the keyring.")
