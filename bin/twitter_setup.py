#!/usr/bin/env python3

# This function of Scitify is used to securely set up Twitter API credentials by reading them from a txt file and storing them in the keyring.
# Example usages are as the following:
# python3 twitter_setup.py --service_name twitter_credentials
# The credentials will be securely stored under the service name provided by the user.

# Note: The '/Scitify/config/twitter_API.txt' file is required and must contain the following fields:
# bearer_token, api_key, api_key_secret, access_token, access_token_secret

# Copyright (C) 2024 Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France.
# This code is up to date as of October 2024.

import keyring
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

# Helper function for error handling when missing required fields in the txt file
def validate_txt_file(config):
    required_fields = ['bearer_token', 'api_key', 'api_key_secret', 'access_token', 'access_token_secret']
    missing_fields = [field for field in required_fields if not config.has_option('DEFAULT', field)]
    
    if missing_fields:
        raise ValueError(f"Error: Missing required fields in the txt file: {', '.join(missing_fields)}")

# Custom function to display the help message
def print_help():
    print("""usage: twitter_setup.py [--help] [--service_name SERVICE_NAME]

This function of Scitify is used to securely set up Twitter API credentials by reading them from the '/Scitify/config/twitter_API.txt' file and storing them in the keyring.

Example usage:
  python3 twitter_setup.py --service_name twitter_credentials

Note: Ensure that the '/Scitify/config/twitter_API.txt' file contains the following fields:
  bearer_token, api_key, api_key_secret, access_token, access_token_secret

Created by: Cyan Ching, PhD student at The Physical Chemistry Curie Lab, Institut Curie, France.
Date: October 2024
    """)
    sys.exit()

# Initialize the argument parser without default help
parser = argparse.ArgumentParser(add_help=False)

# Add custom --help flag (no -h shortcut)
parser.add_argument('--help', action='store_true', help="Show this help message and exit.")
parser.add_argument('--service_name', required=False, help="Name to store the credentials under in the keyring (e.g., 'twitter_credentials').")

# Parse arguments
args = parser.parse_args()

# Display help message if --help is provided, before checking other arguments
if args.help:
    print_help()

# Check if --service_name is missing and raise an error manually
if not args.service_name:
    print("Error: --service_name is required. Use --help for more information.")
    sys.exit(1)

# Check if the required file 'twitter_API.txt' exists
file_path = '../config/twitter_API.txt'
if not os.path.exists(file_path):
    print(f"Error: The file '{file_path}' does not exist.")
    sys.exit(1)

# Read the credentials from the txt file
config = configparser.ConfigParser(interpolation=None)
config.read(file_path)

# Validate that all required fields are present in the txt file
try:
    validate_txt_file(config)
except ValueError as e:
    print(e)
    sys.exit(1)

# Extract credentials
bearer_token = config.get('DEFAULT', 'bearer_token').strip('"')
api_key = config.get('DEFAULT', 'api_key').strip('"')
api_key_secret = config.get('DEFAULT', 'api_key_secret').strip('"')
access_token = config.get('DEFAULT', 'access_token').strip('"')
access_token_secret = config.get('DEFAULT', 'access_token_secret').strip('"')

# Save the credentials in the keyring
keyring.set_password(args.service_name, "bearer_token", bearer_token)
keyring.set_password(args.service_name, "api_key", api_key)
keyring.set_password(args.service_name, "api_key_secret", api_key_secret)
keyring.set_password(args.service_name, "access_token", access_token)
keyring.set_password(args.service_name, "access_token_secret", access_token_secret)

print(f"Credentials for {args.service_name} have been securely stored in the keyring.")

# Retrieve the credentials from the keyring for verification
bearer_token = keyring.get_password(args.service_name, "bearer_token")
api_key = keyring.get_password(args.service_name, "api_key")
api_key_secret = keyring.get_password(args.service_name, "api_key_secret")
access_token = keyring.get_password(args.service_name, "access_token")
access_token_secret = keyring.get_password(args.service_name, "access_token_secret")

# Check if credentials were retrieved successfully
if all([bearer_token, api_key, api_key_secret, access_token, access_token_secret]):
    print(f"Credentials for {args.service_name} retrieved successfully:")
    print(f"Bearer Token: {bearer_token}")
    print(f"API Key: {api_key}")
    print(f"API Key Secret: {api_key_secret}")
    print(f"Access Token: {access_token}")
    print(f"Access Token Secret: {access_token_secret}")
else:
    print("Failed to retrieve one or more credentials.")






