# Scitify

Scitify is a custom tool designed to automatically retrieve the latest scientific publications based on your specified research interests. It sends notifications via email (currently supports sending from Outlook and Gmail accounts, but can send to any email service) and/or Twitter (operating as a bot posting paper updates). Scitify currently powers the [@Pha_Tran_Papers](https://x.com/pha_tran_papers) bot on Twitter (referred to as "X" by some), though for convenience, I'll keep referring to it as Twitter.

## Features

### Supported Sources

Scitify retrieves the latest publications based on days before today from the following sources: 

1. [arXiv](https://arxiv.org/)
2. [bioRxiv](https://www.biorxiv.org/)
3. [PubMed](https://pubmed.ncbi.nlm.nih.gov/)

You can choose to retrieve from one or more of these sources. 

### Notifications

You have the option to receive updates via: 

1. Email (can send from Outlook or Gmail to any specified email address).
2. And/or Twitter posts (posts updates as a Twitter bot).

### Automated Scheduling

Scitify can be set to automatically retrieve publications at defined intervals:
1. Every x minutes, hours, or days
2. At a specific time each day
3. At a specific time every x days

Scitify can run on a fully automated schedule with minimal CPU usage. After setup, no further manual intervention is needed if the search criteria are properly configured.

### Customizable Keyword Search

Define retrieval criteria using the following types of keywords:
1. Search keywords: Required for finding relevant papers.
2. Exclusion keywords: Exclude publications with these terms in the title or abstract.
3. Required keywords: Ensure that certain keywords are always present.

For PubMed, you can also specify journals of interest (note: bioRxiv and arXiv are not available for journal-specific searches). Only search keywords are required, while exclusion and required keywords are optional but recommended for more accurate results.

### Email Content

In the email notifications you receive, you will get:
- A list of publication titles with corresponding URLs
- Text files (one file per source) containing titles, authors, URLs, and abstracts.

For Twitter posts, only the title and URL are included.

## Folder Structure

`/bin`: Contains all Scitify code for retrieving publications and sending notifications. The individual scripts for these tasks are kept as standalone scripts, designed to be set up once for automated operation without frequent manual use.
`/config`: Contains configuration files where you can specify your keywords and other options (such as sources to search from, email, or Twitter settings).
`/output`: Temporarily stores the retrieved data, such as publication titles, abstracts, and URLs. This data is cleared once notifications are sent.
`/logs`: Contains logs of the latest retrievals and notifications, allowing you to track the status of each operation. The log files are automatically renewed with each retrieval, so only the most recent log is kept.

## Dependencies

The following dependencies are not included by default in `Python`, please make sure they are installed correctly.
```
pip install feedparser requests biopython keyring tweepy
```

## Usage

To use Scitify, clone this repository.
```
pip install feedparser requests biopython keyring tweepy
```

navigate to the bin folder and run the individual Python scripts or use the provided bash scripts to automate the full process. Each script includes a --help flag that provides detailed usage instructions and examples.

Example commands:

    To retrieve publications:

    bash

python3 arXiv_retrieve.py --days_before_today 7 --batch_size 200

To set up scheduled retrievals:

bash

bash scheduler.sh --time 14:30  # Runs the retrieval daily at 14:30

To get help for each script:

bash

    python3 email_papers.py --help

Credentials Management

Scitify also includes scripts to securely store and retrieve your email and Twitter credentials using keyrings. These scripts are provided in the bin folder for easy setup.
Additional Information

    The bash scripts included in the repository are used to tie together the individual Python scripts for fully automated operation. They also include their own --help flags.
    Scitify is flexible and designed so that users only need to set it up once for automatic updates. Afterward, the tool can run independently and notify you of new publications.

sudo tar -xf ~/Downloads/ctffind-4.1.14-patched.tar.gz -C /usr/local/
```
