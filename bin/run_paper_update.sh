#!/bin/bash

# This Scitify function is used to collectively retrieve paper updates from arXiv, bioRxiv, and PubMed, then send the updates via email and/or Twitter.
# Usage examples:
#   bash ./run_paper_update.sh
#   bash ./run_paper_update.sh 5
# The number specifies the maximum number of connection attempts to retrieve papers from journals. Default is 3 if not specified.

# ----------------------------------------------------------------------------------------

# Copyright (C) 2024 Cyan Ching, PhD student at The Physical Chemistry Curie Lab, Institut Curie, France.
# This code is up to date as of October 2024.

# ----------------------------------------------------------------------------------------

# Function to print the header in Bash
print_header() {
    echo "     ______                _            "
    echo "    \  ___)              | |           "
    echo "     \ \__   ___ ___ _  _| |_  _  _  _ "
    echo "      > > \ / / (   ) |/     \| || || |"
    echo "     / /_\ v /| || || ( (| |) ) \| |/ |"
    echo "    /_____> <  \_)\_)\_)_   _/ \_   _/ "
    echo "         / ^ \           | |     | |   "
    echo "        /_/ \_\          |_|     |_|   "
    echo
    echo "    Welcome to Scitify - Your Custom Scientific Paper Retriever!"
    echo
    echo "    Author: Cyan Ching, PhD Student at Institut Curie"
    echo "    Version: 1.0 | Date: October 2024"
    echo
}

# Call the print_header function at the start of the script
print_header

# Function to remove the header and extra blank lines from the output
clean_output() {
    awk 'BEGIN { skipping=0; prev_blank=0 } 
        /______/ { skipping=1 } 
        /Version:/ { skipping=0; next } 
        !skipping { 
            if (NF > 0) { print; prev_blank=0 } 
            else if (prev_blank == 0) { prev_blank=1 } 
        }'
}

# Custom help function
function print_help() {
    echo """
    Usage: run_paper_update.sh [max_retry_attempts]

    This Scitify function retrieves paper updates from arXiv, bioRxiv, and PubMed, then sends the updates via email or Twitter.

    Example:
      bash ./run_paper_update.sh 5  # Retry journal retrieval up to 5 times (default is 3)

    Ensure the '/Scitify/config/paper_update_config.txt' file exists and contains valid configuration.
    
    If a journal source (arXiv, bioRxiv, PubMed) is included (inclusion status = 1), ensure that all corresponding inputs (days, batch size, etc.) are provided.
    
    If email sending or Twitter posting is enabled, ensure that all required inputs (service, receiver email, credentials, etc.) are filled in. 
    
    At least one journal source and one output function (email or Twitter) must be enabled (status = 1 in the config file).

    Created by: Cyan Ching, PhD student at The Physical Chemistry Curie Lab, Institut Curie, France.
    Date: October 2024
    """
    exit 0
}

# If --help is requested
if [[ "$1" == "--help" ]]; then
    print_help
fi

# ----------------------------------------------------------------------------------------

# Load parameters from the configuration file
config_file="../config/paper_update_config.txt"

# Check if the config file exists
if [ ! -f "$config_file" ]; then
    echo "Configuration file not found: $config_file"
    exit 1
fi

# Initialize variables for validation
missing_params=()

# Read values from the configuration file
while IFS="=" read -r key value
do
    # Ignore comments and empty lines
    if [[ "$key" =~ ^#.*$ || -z "$key" ]]; then
        continue
    fi

    # Remove any surrounding quotes
    value=$(echo "$value" | sed 's/^"//;s/"$//')

    # Dynamically assign variables based on key
    case "$key" in
        include_arXiv) include_arXiv="$value" ;;
        days_arXiv) days_arXiv="$value" ;;
        batch_arXiv) batch_arXiv="$value" ;;
        
        include_bioRxiv) include_bioRxiv="$value" ;;
        days_bioRxiv) days_bioRxiv="$value" ;;
        batch_bioRxiv) batch_bioRxiv="$value" ;;
        
        include_PubMed) include_PubMed="$value" ;;
        days_PubMed) days_PubMed="$value" ;;
        batch_PubMed) batch_PubMed="$value" ;;
        email_PubMed) email_PubMed="$value" ;;
        
        send_email) send_email="$value" ;;
        service) service="$value" ;;
        receiver_email) receiver_email="$value" ;;
        post_tweet) post_tweet="$value" ;;
        credentials) twitter_credentials="$value" ;;
    esac
done < "$config_file"

# ----------------------------------------------------------------------------------------

# Check if all retrievals are disabled, and track errors
if [ "$include_arXiv" -eq 0 ] && [ "$include_bioRxiv" -eq 0 ] && [ "$include_PubMed" -eq 0 ]; then
    error_messages+=("Error: All journal retrievals are disabled. Please enable at least one journal retrieval (arXiv, bioRxiv, or PubMed).")
fi

# Ensure at least one of send_email or post_tweet is enabled, and track errors
if [ "$send_email" -eq 0 ] && [ "$post_tweet" -eq 0 ]; then
    error_messages+=("Error: Both 'send_email' and 'post_tweet' are disabled. At least one must be enabled.")
fi

# Print and exit if there are any errors
if [ ${#error_messages[@]} -gt 0 ]; then
    for error in "${error_messages[@]}"; do
        echo "$error"
    done
    exit 1
fi

# ----------------------------------------------------------------------------------------

# Check required parameters for each source based on inclusion
if [ -n "$include_arXiv" ] && [ "$include_arXiv" -eq 1 ]; then
    if [ -z "$days_arXiv" ] || [ -z "$batch_arXiv" ]; then
        echo "Error: Missing required values for arXiv (days_arXiv, batch_arXiv) in the configuration file."
        exit 1
    fi
else
    echo "arXiv retrieval is disabled."
fi

if [ -n "$include_bioRxiv" ] && [ "$include_bioRxiv" -eq 1 ]; then
    if [ -z "$days_bioRxiv" ] || [ -z "$batch_bioRxiv" ]; then
        echo "Error: Missing required values for bioRxiv (days_bioRxiv, batch_bioRxiv) in the configuration file."
        exit 1
    fi
else
    echo "bioRxiv retrieval is disabled."
fi

if [ -n "$include_PubMed" ] && [ "$include_PubMed" -eq 1 ]; then
    if [ -z "$days_PubMed" ] || [ -z "$batch_PubMed" ] || [ -z "$email_PubMed" ]; then
        echo "Error: Missing required values for PubMed (days_PubMed, batch_PubMed, email_PubMed) in the configuration file."
        exit 1
    fi
else
    echo "PubMed retrieval is disabled."
fi

# ----------------------------------------------------------------------------------------

# Check required parameters if send_email is enabled
if [ "$send_email" -eq 1 ]; then
    if [ -z "$service" ] || [ -z "$receiver_email" ]; then
        echo "Error: Missing required parameters for email sending (service, receiver_email)."
        exit 1
    fi
fi

# Check required parameters if post_tweet is enabled
if [ "$post_tweet" -eq 1 ]; then
    if [ -z "$twitter_credentials" ]; then
        echo "Error: Missing required parameter for Twitter posting (twitter_credentials)."
        exit 1
    fi
fi

# ----------------------------------------------------------------------------------------

# Define the retry count for arXiv_retrieve.py (default to 3 if not specified)
retry_count=${1:-3}

# Run arXiv_retrieve.py if arXiv inclusion is enabled
if [ -n "$include_arXiv" ] && [ "$include_arXiv" -eq 1 ]; then
    for ((i=1; i<=$retry_count; i++))
    do
        echo "Attempt $i to retrieve publications from arXiv (running arXiv_retrieve.py)"
        python3 arXiv_retrieve.py --days_before_today $days_arXiv --batch_size $batch_arXiv --quiet 2>&1 | clean_output
        arxiv_status=$?
        
        # Check if the output file exists and is not empty
        if [ -s "../output/latest_arxiv_entries.txt" ]; then
            echo "Retrieval from arXiv succeeded on attempt $i"
            break
        else
            echo "No entries returned from arXiv, retrying..."
        fi

        # If this was the last attempt, continue without exiting
        if [ $i -eq $retry_count ]; then
            echo "Retrieval from arXiv failed after $retry_count attempts"
        fi
    done
fi

# Run bioRxiv_retrieve.py if bioRxiv inclusion is enabled
if [ -n "$include_bioRxiv" ] && [ "$include_bioRxiv" -eq 1 ]; then
    for ((i=1; i<=$retry_count; i++)); do
        echo "Attempt $i to retrieve publications from bioRxiv (running bioRxiv_retrieve.py)"
        python3 bioRxiv_retrieve.py --days_before_today $days_bioRxiv --batch_size $batch_bioRxiv --quiet 2>&1 | clean_output
        bioRxiv_status=$?

        # Check if the output file exists and is not empty
        if [ -s "../output/latest_bioRxiv_entries.txt" ]; then
            echo "Retrieval from bioRxiv succeeded on attempt $i"
            break
        else
            echo "No entries returned from bioRxiv, retrying..."
        fi

        # If this was the last attempt, continue without exiting
        if [ $i -eq $retry_count ]; then
            echo "Retrieval from bioRxiv failed after $retry_count attempts"
        fi
    done
fi

# Run PubMed_retrieve.py if PubMed inclusion is enabled
if [ -n "$include_PubMed" ] && [ "$include_PubMed" -eq 1 ]; then
    for ((i=1; i<=$retry_count; i++)); do
        echo "Attempt $i to retrieve publications from PubMed (running PubMed_retrieve.py)"
        python3 PubMed_retrieve.py --days_before_today $days_PubMed --batch_size $batch_PubMed --email $email_PubMed --quiet 2>&1 | clean_output
        PubMed_status=$?

        # Check if the output file exists and is not empty
        if [ -s "../output/latest_pubmed_entries.txt" ]; then
            echo "Retrieval from PubMed succeeded on attempt $i"
            break
        else
            echo "No entries returned from PubMed, retrying..."
        fi

        # If this was the last attempt, continue without exiting
        if [ $i -eq $retry_count ]; then
            echo "Retrieval from PubMed failed after $retry_count attempts"
        fi
    done
fi

# ----------------------------------------------------------------------------------------
# Run summarise_papers.py before email or tweet
echo
echo "Summarising retrieved publications (running summarise_papers.py)..."
python3 summarise_papers.py 2>&1 | clean_output
summarise_status=$?
if [ $summarise_status -ne 0 ]; then
    echo "Summarisation of retrieved publications failed with the following error:"
    echo "$summarise_status"
fi

# ----------------------------------------------------------------------------------------

email_status="not run"
tweet_status="not run"

# If email sending is enabled
if [ "$send_email" -eq 1 ]; then
    echo
    echo "Preparing to send the summary of retrieved publications to your specified email address (running email_papers.py)..."
    python3 email_papers.py --service $service --receiver_email $receiver_email 2>&1 | clean_output
    email_papers_status=$?
    if [ $email_papers_status -ne 0 ]; then
        echo "Email sending failed with the following error:"
        echo "$email_papers_status"
        email_status="failed"
    else
        email_status="success"
    fi
fi

# If Twitter posting is enabled
if [ "$post_tweet" -eq 1 ]; then
    echo
    echo "Preparing to send the summary of retrieved publications to your specified Twitter account (running twitter_papers.py)..."
    python3 twitter_papers.py --credentials_key $twitter_credentials 2>&1 | clean_output
    twitter_papers_status=$?
    if [ $twitter_papers_status -ne 0 ]; then
        echo "Posting on Twitter failed with the following error:"
        echo "$twitter_papers_status"
        tweet_status="failed"
    else
        tweet_status="success"
    fi
fi

# ----------------------------------------------------------------------------------------

# Report final status
echo
echo "Summary of operations:"
if [ "$send_email" -eq 1 ]; then
    echo "Email status: $email_status"
fi
if [ "$post_tweet" -eq 1 ]; then
    echo "Twitter posting status: $tweet_status"
fi

echo
echo "All Scitify functions completed!"
echo

# List of files to check and remove if they exist
files=("../output/latest_arxiv_entries.txt" "../output/latest_bioRxiv_entries.txt" "../output/latest_pubmed_entries.txt" "../output/titles_and_urls.txt")

# Loop through each file and check if it exists, then remove it
for file in "${files[@]}"
do
    if [ -f "$file" ]; then
        echo "Removing $file..."
        rm "$file"
    else
        echo "$file does not exist."
    fi
done



