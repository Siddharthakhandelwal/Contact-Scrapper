# Professional Email Lead Extractor

A Python command-line tool for extracting and managing professional email leads based on specific roles. The tool searches multiple sources, validates emails, prevents duplicates, and stores results in CSV format.

## Features

- **Multi-source extraction**: Searches Google and LinkedIn for professional contacts
- **Role-based filtering**: Targets specific professional roles (Real Estate, Finance, Business, etc.)
- **Duplicate prevention**: Automatically skips existing leads
- **Email validation**: Ensures high-quality, professional email addresses
- **CSV storage**: Organized data storage with comprehensive lead information
- **Progress tracking**: Real-time feedback during extraction process
- **Error handling**: Robust error handling with detailed logging
- **Rate limiting**: Respectful scraping with configurable delays

## Installation

1. **Clone or download the project files**

2. **Install required dependencies**:
   ```bash
   pip install requests beautifulsoup4 pandas trafilatura
   ```

3. **Create necessary directories**:
   ```bash
   mkdir logs
   ```

## Usage

### Basic Usage

Run the script to extract leads for all predefined roles:

```bash
python email_lead_extractor.py
