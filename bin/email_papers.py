#!/usr/bin/env python3

# This Scitify function is used to securely send the '/Scitify/output/titles_and_urls.txt' file content as the main body of an email and attach the '/Scitify/output/latest_arxiv_entries.txt', '/Scitify/output/latest_bioRxiv_entries.txt', and '/Scitify/output/latest_pubmed_entries.txt' files (if they exist).
# Usage examples:
#   python3 email_papers.py --service gmail_service --receiver_email your_email
#   python3 email_papers.py --service outlook_service --receiver_email your_email
#
# Note: Ensure you have already set up your email credentials using 'email_setup.py'.
#
# Copyright (C) 2024 Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France.
# This code is up to date as of October 2024.

import argparse
import keyring
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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

# Helper function to display the help message in the desired format
def print_help():
    help_message = """usage: email_papers.py [--help] --service {outlook_service,gmail_service} --receiver_email RECEIVER_EMAIL

This function of Scitify is used to securely send the '/Scitify/output/titles_and_urls.txt' file content as the main body of the email and attach the '/Scitify/output/latest_arxiv_entries.txt', '/Scitify/output/latest_bioRxiv_entries.txt', and '/Scitify/output/latest_pubmed_entries.txt' files (if they exist).

Example usages:
  python3 email_papers.py --service gmail_service --receiver_email your_email
  python3 email_papers.py --service outlook_service --receiver_email your_email

Note: Ensure you have already set up your email credentials using 'email_setup.py'.

Created by: Cyan Ching, PhD student at The Physical Chemistry Curie Lab, Institut Curie, France.
Date: October 2024
"""
    print(help_message)
    sys.exit()

# Initialize argument parser without default help
parser = argparse.ArgumentParser(add_help=False)

# Add custom --help flag
parser.add_argument('--help', action='store_true', help="Show this help message and exit.")
parser.add_argument('--service', required=False, choices=['outlook_service', 'gmail_service'],
                    help="Specify the email service to use: either 'outlook_service' or 'gmail_service'.")
parser.add_argument('--receiver_email', required=False, help="The email address to receive the updates.")

# Parse arguments
args = parser.parse_args()

# Display custom help if --help is provided
if args.help:
    print_help()

# Check for missing flags
if not args.service or not args.receiver_email:
    print("Error: --service and --receiver_email are required. Use --help for more information.")
    sys.exit(1)

# Check if the 'titles_and_urls.txt' file exists
main_file = "../output/titles_and_urls.txt"
if not os.path.exists(main_file):
    print(f"Error: '{main_file}' does not exist. Please generate it before sending the email.")
    sys.exit(1)

# Retrieve email credentials from keyring
sender_email = keyring.get_password(args.service, "email_username")
password = keyring.get_password(args.service, "email_password")

if not sender_email or not password:
    print(f"Failed to retrieve credentials for {args.service}. Please set them using 'email_setup.py'.")
    sys.exit(1)

receiver_email = args.receiver_email

# Read the content of 'titles_and_urls.txt'
with open(main_file, 'r') as f:
    email_body = f.read()

# Setup the MIME (create the 'message' object before attachments)
message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = "Titles and URLs from the Latest Articles"

# Attach any of the latest_arxiv_entries.txt, latest_bioRxiv_entries.txt, and latest_pubmed_entries.txt if they exist
attachment_files = ["../output/latest_arxiv_entries.txt", "../output/latest_bioRxiv_entries.txt", "../output/latest_pubmed_entries.txt"]

missing_files = []
for attachment_file in attachment_files:
    if os.path.exists(attachment_file):
        try:
            with open(attachment_file, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={os.path.basename(attachment_file)}")
            message.attach(part)
            print(f"Attached: {attachment_file}")
        except Exception as e:
            print(f"Failed to attach {attachment_file}: {e}")
    else:
        missing_files.append(attachment_file)

# If any files are missing, add a message that no entries were found from arXiv, bioRxiv, or PubMed
if missing_files:
    missing_sources = []
    for file in missing_files:
        if "arxiv" in file.lower():
            missing_sources.append("arXiv")
        elif "biorxiv" in file.lower():
            missing_sources.append("bioRxiv")
        elif "pubmed" in file.lower():
            missing_sources.append("PubMed")
    
    missing_sources_info = "\n".join([f"No entries found from {source}." for source in missing_sources])
    email_body += f"\n\n{missing_sources_info}"

# Attach the updated email body
message.attach(MIMEText(email_body, 'plain'))

# SMTP server setup
smtp_server = "smtp.office365.com" if args.service == "outlook_service" else "smtp.gmail.com"
smtp_port = 587

# Connect to the SMTP server and send the email
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
    print(f"Email successfully sent to {receiver_email}.")
except Exception as e:
    print(f"Failed to send email: {e}")








