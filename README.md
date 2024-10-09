# Scitify

```  ______                _            
    \  ___)              | |           
     \ \__   ___ ___ _  _| |_  _  _  _ 
      > > \ / / (   ) |/     \| || || |
     / /_\ v /| || || ( (| |) ) \| |/ |
    /_____> <  \_)\_)\_)_   _/ \_   _/ 
         / ^ \           | |     | |   
        /_/ \_\          |_|     |_| 
```

Scitify is a custom tool designed to automatically retrieve the latest scientific publications based on your specified research interests. It sends notifications via email (currently supports sending from Outlook and Gmail accounts, but can send to any email service) and/or Twitter (operating as a bot posting paper updates). Scitify currently powers the [@Pha_Tran_Papers](https://x.com/pha_tran_papers) bot set up and managed by [me](https://x.com/chingcyan) on Twitter (referred to as "X" by some), though for convenience, I'll keep referring to it as Twitter.

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

### To use Scitify, clone this repository.
```
git clone https://github.com/cyanching/Scitify.git
```
### Next, enter the directory.
```
cd Scitify
```
### Explore available functions in `/bin`
The description, usage, options, and use examples of every function (`Python` or `Shell` script, since they are not meant to be used routinely, they are kept as scripts) can be queried with the `--help` flag, they can each be used individually if needed.

### Edit the following files in `/config` to set up configurations for retrieval from one or more of them:
`arXiv_keywords.txt`

`bioRxiv_keywords.txt`

`PubMed_keywords.txt`

These files are now pre-filled for retrieving paper updates about the phase transition of biomolecules as a use example.

### Set up your email credentials securely in `/bin`
```
python3 email_setup.py --email your_email --password your_password --service outlook_service
```
or if you prefer Gmail
```
python3 email_setup.py --email your_email --password your_password --service gmail_service
```
If you have two-factor authentication set up, which is common for Gmail, you need to acquire an `App password` instead of using your Google account password.

### Set up your Twitter credentials securely in `/bin`
1. Hold or register a Twitter developer account.
2. Set up a new project in your Twitter developer account.
3. In the app details, ensure you have at least "Read and Write" permissions in the authentication settings.
4. Generate the following in the "Keys and Tokens" section:

- `bearer_token`

- `api_key`

- `api_key_secret`

- `access_token`

- `access_token_secret`

Fill these values into `twitter_API.txt` in `/config`, and do the following.
```
python3 twitter_papers.py --credentials_key twitter_credentials
```
Make sure your `twitter_API.txt` is deleted or stored safely after the setup.

### Receive notifications of retrieved results
1. Fill in retrieval and notification specifications in `paper_update_config.txt` found in `/config`.
2. Then run `run_paper_update.sh` in `/bin` as the following to readily receive notifications of retrieved results.
```
bash ./run_paper_update.sh
```
3. To set up scheduled notifications, run the following in `/bin` to receive daily updates at 14:30.
```
nohup bash ./scheduler.sh --time 14:30 &
```
To specify other types of frequency settings, check options available with:
```
bash ./scheduler.sh --help
```
For more robust automated operation (e.g., in case of machine restart), you are recommended to set up a `crontab` or a `systemd timer` yourself.

## Follow the author

If you enjoy using Scitify, I'd love to know! You can reach out to me for scientific discussions and collaboration via my listed means of contact on my [site](https://cyanching.github.io/). 


