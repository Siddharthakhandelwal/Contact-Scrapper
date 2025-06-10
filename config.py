import os
from datetime import datetime

# Professional roles to search for
ROLES = [
    # Real Estate
    "Realtor", "Real Estate Agent", "Real Estate Broker", "Real Estate Investor", "Property Manager",
    "Real Estate Developer", "Mortgage Broker", "Loan Officer", "Mortgage Insurance Agent", "Title Agent",
    "Real Estate Attorney", "Appraiser", "Home Inspector", "Escrow Officer", "Commercial Real Estate Agent",
    "Luxury Real Estate Agent", "Real Estate Photographer", "Real Estate Videographer", "Real Estate Coach",
    "Real Estate Mentor", "Real Estate Syndicator", "Short-Term Rental Manager", "Airbnb Manager",
    "Real Estate Influencer",

    # Mixed Niches
    "Startup Founder", "Entrepreneur", "Business Coach", "Podcast Host", "YouTuber", "Content Creator",
    "Influencer", "Health Coach", "Fitness Trainer", "Nutritionist", "Life Coach", "Public Speaker",
    "Author", "Course Creator", "Digital Marketer", "Marketing Consultant", "Consultant",
    "Personal Brand Strategist", "E-commerce Business Owner", "Dropshipping Expert", "Shopify Store Owner",
    "Angel Investor", "Venture Capitalist",

    # Banking & Finance
    "Private Banker", "Wealth Manager", "Financial Advisor", "Investment Banker", "Credit Analyst",
    "Bank Branch Manager", "Commercial Banker", "Retail Banker", "Fintech Founder", "Fintech Executive",
    "Hedge Fund Manager", "Risk Management Consultant", "Insurance Agent", "Treasury Analyst",
    "Corporate Finance Consultant", "Estate Planner", "Tax Consultant", "Financial Planner",
    "CFA", "CPA", "Finance Coach"
]

# File paths
CSV_FILE_PATH = "email_leads.csv"
LOG_FILE_PATH = f"logs/email_lead_extractor_{datetime.now().strftime('%Y%m%d')}.log"

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Rate limiting settings
DEFAULT_DELAY_BETWEEN_SEARCHES = 2.0  # seconds
DEFAULT_MAX_LEADS_PER_ROLE = 10

# API Keys (if needed)
GOOGLE_API_KEY = ""
GOOGLE_CSE_ID = ""

# User agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Maximum retries for failed requests
MAX_RETRIES = 3

# Timeout for web requests (seconds)
REQUEST_TIMEOUT = 30
