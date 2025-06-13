# Email Lead Harvester and Sender

A comprehensive tool for extracting email leads from various sources and sending personalized emails to them. This project consists of two main components: an email lead extractor and an email sender.

## Features

### Email Lead Extractor
- Extracts email leads from multiple sources
- Categorizes leads by professional roles
- Filters leads by specific countries
- Stores leads in a structured CSV format
- Includes verification status for each lead
- Supports various professional categories:
  - Real Estate professionals
  - Business coaches and entrepreneurs
  - Banking & Finance professionals
  - And many more

### Country-Based Filtering
- Pre-configured target countries:
  - United States
  - Canada
  - United Kingdom
  - Australia
  - New Zealand
  - Germany
  - Netherlands
  - France
  - United Arab Emirates
  - Kuwait
  - Bahrain
- Intelligent country name matching
- Detailed country-wise statistics
- Automatic location detection and filtering

### Email Sender
- Sends personalized emails to extracted leads
- Tracks email sending status
- Implements rate limiting to prevent spam flags
- Supports bulk email sending with configurable limits
- Maintains detailed logs of email sending activities

## Project Structure

```
EmailHarvester/
├── email_lead_extractor.py           # Original lead extractor
├── country_based_email_extractor.py  # Country-filtered lead extractor
├── email_sender.py                   # Script for sending emails to leads
├── config.py                         # Configuration settings
├── email_leads.csv                   # Database of extracted leads
├── extractors/                       # Directory containing extractor modules
├── utils/                            # Utility functions
└── logs/                             # Log files directory
```

## Quick Installation

Install all required packages with a single command:
```bash
pip3 install requests beautifulsoup4 pandas trafilatura geopy
```

## Configuration

### Email Sender Configuration
Edit the `email_sender.py` file to configure your email settings:

```python
SMTP_SERVER = "smtp.gmail.com"  # Your SMTP server
SMTP_PORT = 587                 # Your SMTP port
SENDER_EMAIL = "your-email@gmail.com"  # Your email address
SENDER_PASSWORD = "your-app-password"  # Your email password or app password
```

For Gmail users:
1. Enable 2-factor authentication in your Google Account
2. Generate an App Password:
   - Go to Google Account Settings
   - Security
   - 2-Step Verification
   - App Passwords
   - Generate a new app password for "Mail"

## Usage

### Extracting Leads (Country-Based)
Run the country-based lead extractor:
```bash
python country_based_email_extractor.py
```

This will:
- Search for leads based on configured roles
- Filter leads by predefined target countries
- Extract and verify email addresses
- Save leads to `email_leads.csv`
- Show detailed country-wise statistics

Command-line options:
```bash
# List all available roles
python country_based_email_extractor.py --list-roles

# Search for specific roles
python country_based_email_extractor.py --roles "Real Estate Agent" "Property Manager"

# Adjust number of leads per role
python country_based_email_extractor.py --max-leads 20

# Adjust delay between searches
python country_based_email_extractor.py --delay 3.0
```

### Original Lead Extractor
Run the original lead extractor:
```bash
python email_lead_extractor.py
```

### Sending Emails
Run the email sender:
```bash
python email_sender.py
```

This will:
- Process up to 450 unsent leads
- Send personalized emails
- Update the CSV with sending status
- Log all activities

## CSV Structure

The `email_leads.csv` file contains the following columns:
- name: Lead's name
- email: Lead's email address
- role: Professional role
- source: Where the lead was found
- profile_url: URL to lead's profile
- company: Company name
- location: Lead's location
- country: Detected country
- date_added: When the lead was added
- verified: Email verification status
- email_status: Email sending status ("Sent" or "Not Sent")
- email_sent_date: When the email was sent

## Best Practices

1. **Rate Limiting**
   - The script includes a 2-second delay between emails
   - Adjust this delay based on your email provider's limits

2. **Email Content**
   - Customize the email template in `email_sender.py`
   - Personalize messages based on the lead's role and company
   - Avoid spam trigger words

3. **Monitoring**
   - Check the logs directory for detailed activity logs
   - Monitor email sending status in the CSV file
   - Review failed email attempts
   - Track country-wise lead distribution

## Security Notes

1. Never commit sensitive information like API keys or passwords
2. Use environment variables for sensitive data
3. Regularly update your app passwords
4. Monitor your email account for any suspicious activity

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
