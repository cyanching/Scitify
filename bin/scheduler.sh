#!/bin/bash

# This Scitify function is used to schedule paper updates by email/Twitter at a specified frequency or time.
# The latest log file is kept in /Scitify/logs/run_paper_update.log.

# ----------------------------------------------------------------------------------------
# Copyright (C) 2024 Cyan Ching, PhD student at The Physical Chemistry Curie Lab of Institut Curie in France.
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
    echo "    Welcome to Scitify - Your Custom New Scientific Publication Notifier!"
    echo
    echo "    Author: Cyan Ching, PhD Student at Institut Curie"
    echo "    Version: 1.0 | Date: October 2024"
    echo
}

# Function to display the help message
function print_help() {
    # Call the print_header function at the start of the script
    print_header
    echo """
    Usage: $0 [options]

    This Scitify function allows you to run the 'run_paper_update.sh' script at flexible intervals. 
    You can specify the frequency in minutes, hours, days, or at a specific time each day 
    or every few days. 

    Options:
      --minutes n          Run the script every n minutes.
      --hours n            Run the script every n hours.
      --days n             Run the script every n days.
      --time hh:mm         Run the script at a specific time every day.
      --time_every_days n hh:mm  Run the script at a specific time every n days.
      --help               Show this help message and exit.

    Examples:
      bash ./scheduler.sh --minutes 30         # Run the script every 30 minutes.
      bash ./scheduler.sh --hours 2            # Run the script every 2 hours.
      bash ./scheduler.sh --days 3             # Run the script every 3 days.
      bash ./scheduler.sh --time 14:30         # Run the script every day at 14:30.
      bash ./scheduler.sh --time_every_days 5 08:00  # Run the script at 08:00 every 5 days.
      
    To run this script in the background, use: nohup bash ./scheduler.sh --time 14:30 &
    To check the status of the process: ps aux | grep scheduler.sh
    To kill the process: kill -9 xxxx, the job index is found to the right of your username

    Created by: Cyan Ching, PhD student at The Physical Chemistry Curie Lab, Institut Curie, France.
    Date: October 2024
    """
    exit 0
}

# Function to run the paper update script and log the output
run_with_logging() {
    log_file="../logs/run_paper_update.log"  # Single log file that gets renewed each time
    echo "Retrieving updates, output will be logged to $log_file"

    # Remove the previous log file if it exists
    if [ -f "$log_file" ]; then
        rm "$log_file"
    fi

    # Run the script and log the output to a new log file
    ./run_paper_update.sh > "$log_file" 2>&1
}

# Parse command-line options
while [[ "$1" != "" ]]; do
    case $1 in
        --minutes )           shift
                              minutes=$1
                              ;;
        --hours )             shift
                              hours=$1
                              ;;
        --days )              shift
                              days=$1
                              ;;
        --time )              shift
                              specified_time=$1
                              ;;
        --time_every_days )   shift
                              days_interval=$1
                              shift
                              specified_time=$1
                              ;;
        --help )              print_help
                              ;;
        * )                   echo "Invalid option: $1"
                              print_help
                              ;;
    esac
    shift
done

# If user specified a frequency in minutes
if [ ! -z "$minutes" ]; then
    echo "Retrieving updates every $minutes minutes."
    while true; do
        run_with_logging
        sleep $(($minutes * 60))  # Convert minutes to seconds and sleep
    done
fi

# If user specified a frequency in hours
if [ ! -z "$hours" ]; then
    echo "Retrieving updates every $hours hours."
    while true; do
        run_with_logging
        sleep $(($hours * 3600))  # Convert hours to seconds and sleep
    done
fi

# If user specified a frequency in days
if [ ! -z "$days" ]; then
    echo "Retrieving updates every $days days."
    while true; do
        run_with_logging
        sleep $(($days * 86400))  # Convert days to seconds and sleep
    done
fi

# If user specified a specific time every day
if [ ! -z "$specified_time" ] && [ -z "$days_interval" ]; then
    echo "Retrieving updates every day at $specified_time."
    while true; do
        current_time=$(date +"%H:%M")

        # If it's earlier than the specified time, sleep until then
        if [[ "$current_time" < "$specified_time" ]]; then
            now=$(date +%s)
            next_run=$(date -d "$specified_time" +%s)
            sleep_seconds=$((next_run - now))
            echo "Current time is earlier than $specified_time. Sleeping for $sleep_seconds seconds until the exact time..." >> ../logs/debug.log
            sleep $sleep_seconds
            run_with_logging
        elif [[ "$current_time" == "$specified_time" ]]; then
            run_with_logging
        fi

        # Calculate time until the next run at the specified time tomorrow
        now=$(date +%s)
        next_run=$(date -d "$specified_time next day" +%s)
        sleep_seconds=$((next_run - now))
        echo "Task completed. Sleeping for $sleep_seconds seconds until the next run at $specified_time tomorrow..." >> ../logs/debug.log
        sleep $sleep_seconds
    done
fi

# If user specified a specific time every n days
if [ ! -z "$specified_time" ] && [ ! -z "$days_interval" ]; then
    echo "Retrieving updates every $days_interval days at $specified_time."
    while true; do
        current_time=$(date +"%H:%M")

        # If it's earlier than the specified time, sleep until then
        if [[ "$current_time" < "$specified_time" ]]; then
            now=$(date +%s)
            next_run=$(date -d "$specified_time" +%s)
            sleep_seconds=$((next_run - now))
            echo "Current time is earlier than $specified_time. Sleeping for $sleep_seconds seconds until the exact time..." >> ../logs/debug.log
            sleep $sleep_seconds
            run_with_logging
        elif [[ "$current_time" == "$specified_time" ]]; then
            run_with_logging
        fi

        # Calculate time until the next run after n days
        now=$(date +%s)
        next_run=$(date -d "$specified_time +$days_interval days" +%s)
        sleep_seconds=$((next_run - now))
        echo "Task completed. Sleeping for $sleep_seconds seconds until the next run at $specified_time in $days_interval days..." >> ../logs/debug.log
        sleep $sleep_seconds
    done
fi

# If no valid options were provided, show the help message
print_help
