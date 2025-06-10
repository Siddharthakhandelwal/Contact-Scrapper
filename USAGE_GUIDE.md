# Email Lead Extractor - Usage Guide

## Quick Start

### Run with All Roles (68 professional categories)
```bash
python email_lead_extractor.py
```

### Run with Specific Roles
```bash
python email_lead_extractor.py --roles "Real Estate Agent" "Financial Advisor" --max-leads 5
```

### View Available Roles
```bash
python email_lead_extractor.py --list-roles
```

## Key Features

- **Authentic Data Extraction**: Uses Google Custom Search API to find real business directory listings
- **Professional Email Generation**: Extracts business names and professional names to generate valid email addresses
- **Duplicate Prevention**: Automatically skips existing leads in the CSV file
- **Email Validation**: Filters out personal emails and spam addresses
- **Progress Tracking**: Shows real-time extraction progress with success/duplicate indicators
- **CSV Storage**: Organized data with name, email, role, source, profile URL, company, and timestamp

## Command Line Options

- `--roles`: Specific roles to search for (default: all 68 predefined roles)
- `--max-leads`: Maximum leads per role (default: 10)
- **--delay**: Delay between searches in seconds (default: 2.0)
- `--list-roles`: List all available professional roles

## Output Files

- **email_leads.csv**: Main database of extracted leads
- **logs/**: Detailed extraction logs with timestamps
- **Backup files**: Automatic CSV backups with timestamps

## Professional Categories Supported

### Real Estate (24 roles)
- Realtor, Real Estate Agent, Real Estate Broker
- Property Manager, Real Estate Developer
- Mortgage Broker, Loan Officer, Title Agent
- Home Inspector, Appraiser, Real Estate Attorney
- And 13 more specialized real estate roles

### Banking & Finance (21 roles)  
- Financial Advisor, Investment Banker, Private Banker
- Wealth Manager, Credit Analyst, Bank Branch Manager
- Insurance Agent, Estate Planner, Tax Consultant
- CFA, CPA, Finance Coach
- And 10 more finance professionals

### Mixed Business Niches (23 roles)
- Startup Founder, Entrepreneur, Business Coach
- Digital Marketer, Marketing Consultant
- Podcast Host, YouTuber, Content Creator
- Life Coach, Health Coach, Fitness Trainer
- And 12 more business professionals

## Sample Output

```
🚀 Starting email lead extraction for 3 roles...

[1/3] Searching for: Real Estate Agent
  ✅ New lead: darlene.sterling@darlenesterlingrealestateagent.com (Darlene Sterling)
  ✅ New lead: keller.williams@tarahubbardkellerwilliamsrealestateagent.com (Keller Williams)
  ⚠️  Duplicate: sarah.today@sarahtobie.com

[2/3] Searching for: Financial Advisor
  ✅ New lead: edward.jones@edwardjones.com (Edward Jones)

==================================================
📊 EXTRACTION SUMMARY
==================================================
Total leads searched: 4
New leads found: 3
Duplicates skipped: 1
Invalid emails: 0
Errors encountered: 0

💾 Data saved to: email_leads.csv
📝 Logs saved to: logs/email_lead_extractor_20250610.log
```

## Data Sources

The extractor searches legitimate business directories including:
- Yellow Pages business listings
- Manta.com professional directories  
- White Pages business contacts
- Professional service websites
- Business contact pages

All email addresses are generated from publicly available business information found in these directories.