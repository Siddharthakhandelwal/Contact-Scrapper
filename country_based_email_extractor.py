import argparse
import sys
import time
from typing import List, Dict, Any, Set
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import re

from config import ROLES, CSV_FILE_PATH, LOG_FILE_PATH
from utils.logger import setup_logger
from utils.csv_manager import CSVManager
from utils.email_validator import EmailValidator
from extractors.google_search_extractor import GoogleSearchExtractor
from extractors.linkedin_extractor import LinkedInExtractor


# Predefined list of target countries
TARGET_COUNTRIES = {
    "Canada",
    "United States",
    "New Zealand",
    "Australia",
    "United Kingdom",
    "Germany",
    "Netherlands",
    "France",
    "United Arab Emirates",
    "Kuwait",
    "Bahrain"
}

# Country name mappings for better matching
COUNTRY_MAPPINGS = {
    "USA": "United States",
    "US": "United States",
    "UAE": "United Arab Emirates",
    "UK": "United Kingdom",
    "England": "United Kingdom",
    "Scotland": "United Kingdom",
    "Wales": "United Kingdom",
    "Northern Ireland": "United Kingdom",
    "Holland": "Netherlands",
    "NZ": "New Zealand",
    "AUS": "Australia",
    "DE": "Germany",
    "FR": "France",
    "KW": "Kuwait",
    "BH": "Bahrain"
}


class CountryBasedEmailExtractor:
    """Main class for orchestrating email lead extraction with country filtering."""
    
    def __init__(self):
        self.logger = setup_logger('country_based_email_extractor', LOG_FILE_PATH)
        self.csv_manager = CSVManager(CSV_FILE_PATH)
        self.email_validator = EmailValidator()
        self.extractors = [
            GoogleSearchExtractor(),
            LinkedInExtractor()
        ]
        self.geolocator = Nominatim(user_agent="email_lead_extractor")
        
    def normalize_country_name(self, country: str) -> str:
        """
        Normalize country name using mappings.
        
        Args:
            country: Country name to normalize
            
        Returns:
            Normalized country name
        """
        country = country.strip()
        return COUNTRY_MAPPINGS.get(country, country)
        
    def get_country_from_location(self, location: str) -> str:
        """
        Extract country from a location string using geocoding.
        
        Args:
            location: Location string to extract country from
            
        Returns:
            Country name or empty string if not found
        """
        try:
            # Clean the location string
            location = re.sub(r'[^\w\s,]', '', location)
            
            # Try to geocode the location
            location_data = self.geolocator.geocode(location, exactly_one=True)
            if location_data:
                # Extract country from address
                address = location_data.raw.get('address', {})
                country = address.get('country', '')
                return self.normalize_country_name(country)
            return ''
        except GeocoderTimedOut:
            self.logger.warning(f"Geocoding timed out for location: {location}")
            return ''
        except Exception as e:
            self.logger.error(f"Error geocoding location {location}: {e}")
            return ''
    
    def extract_leads(self, 
                     roles: List[str], 
                     max_leads_per_role: int = 10, 
                     delay_between_searches: float = 2.0) -> Dict[str, Any]:
        """
        Extract email leads for specified roles from target countries.
        
        Args:
            roles: List of professional roles to search for
            max_leads_per_role: Maximum number of leads to extract per role
            delay_between_searches: Delay between searches to avoid rate limiting
            
        Returns:
            Dictionary containing extraction statistics
        """
        stats = {
            'total_searched': 0,
            'new_leads_found': 0,
            'duplicates_skipped': 0,
            'invalid_emails': 0,
            'wrong_country': 0,
            'errors': 0,
            'countries_found': {}
        }
        
        self.logger.info(f"Starting lead extraction for {len(roles)} roles in {len(TARGET_COUNTRIES)} target countries")
        print(f"🚀 Starting email lead extraction for {len(roles)} roles in {len(TARGET_COUNTRIES)} target countries...")
        print("\nTarget Countries:")
        for country in sorted(TARGET_COUNTRIES):
            print(f"  • {country}")
        
        for i, role in enumerate(roles, 1):
            print(f"\n[{i}/{len(roles)}] Searching for: {role}")
            self.logger.info(f"Searching for role: {role}")
            
            try:
                role_leads = []
                
                # Try each extractor
                for extractor in self.extractors:
                    try:
                        extractor_leads = extractor.extract_emails_for_role(
                            role, max_leads_per_role * 2  # Get more leads to account for country filtering
                        )
                        role_leads.extend(extractor_leads)
                        
                    except Exception as e:
                        self.logger.error(f"Extractor {extractor.__class__.__name__} failed for role {role}: {e}")
                        stats['errors'] += 1
                        continue
                
                # Process found leads
                for lead in role_leads:
                    stats['total_searched'] += 1
                    
                    # Validate email
                    if not self.email_validator.is_valid(lead.get('email', '')):
                        stats['invalid_emails'] += 1
                        self.logger.warning(f"Invalid email skipped: {lead.get('email', '')}")
                        continue
                    
                    # Check for duplicates
                    if self.csv_manager.is_duplicate(lead['email']):
                        stats['duplicates_skipped'] += 1
                        self.logger.info(f"Duplicate email skipped: {lead['email']}")
                        print(f"  ⚠️  Duplicate: {lead['email']}")
                        continue
                    
                    # Check country
                    location = lead.get('location', '')
                    if location:
                        country = self.get_country_from_location(location)
                        if country:
                            if country not in TARGET_COUNTRIES:
                                stats['wrong_country'] += 1
                                self.logger.info(f"Lead from wrong country skipped: {lead['email']} ({country})")
                                print(f"  🌍 Wrong country ({country}): {lead['email']}")
                                continue
                            else:
                                # Track country statistics
                                stats['countries_found'][country] = stats['countries_found'].get(country, 0) + 1
                    
                    # Save new lead
                    if self.csv_manager.add_lead(lead):
                        stats['new_leads_found'] += 1
                        self.logger.info(f"New lead added: {lead['email']}")
                        print(f"  ✅ New lead: {lead['email']} ({lead.get('name', 'Unknown')})")
                    else:
                        stats['errors'] += 1
                    
                    # Check if we've reached the maximum leads for this role
                    if stats['new_leads_found'] >= max_leads_per_role:
                        break
                
                # Rate limiting
                if i < len(roles):
                    time.sleep(delay_between_searches)
                    
            except Exception as e:
                self.logger.error(f"Error processing role {role}: {e}")
                stats['errors'] += 1
                print(f"  ❌ Error processing {role}: {e}")
        
        return stats
    
    def display_summary(self, stats: Dict[str, Any]):
        """Display extraction summary."""
        print(f"\n{'='*50}")
        print("📊 EXTRACTION SUMMARY")
        print(f"{'='*50}")
        print(f"Total leads searched: {stats['total_searched']}")
        print(f"New leads found: {stats['new_leads_found']}")
        print(f"Duplicates skipped: {stats['duplicates_skipped']}")
        print(f"Invalid emails: {stats['invalid_emails']}")
        print(f"Wrong country: {stats['wrong_country']}")
        print(f"Errors encountered: {stats['errors']}")
        
        print("\n🌍 Leads by Country:")
        for country, count in sorted(stats['countries_found'].items()):
            print(f"  • {country}: {count}")
        
        print(f"\n💾 Data saved to: {CSV_FILE_PATH}")
        print(f"📝 Logs saved to: {LOG_FILE_PATH}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract professional email leads based on specific roles from predefined target countries"
    )
    parser.add_argument(
        '--roles', 
        nargs='+', 
        help='Specific roles to search for (default: all predefined roles)'
    )
    parser.add_argument(
        '--max-leads', 
        type=int, 
        default=10,
        help='Maximum leads per role (default: 10)'
    )
    parser.add_argument(
        '--delay', 
        type=float, 
        default=2.0,
        help='Delay between searches in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--list-roles', 
        action='store_true',
        help='List all available roles and exit'
    )
    
    args = parser.parse_args()
    
    if args.list_roles:
        print("Available roles:")
        for i, role in enumerate(ROLES, 1):
            print(f"  {i:2d}. {role}")
        return
    
    # Determine which roles to search
    search_roles = args.roles if args.roles else ROLES
    
    # Validate roles
    if args.roles:
        invalid_roles = [role for role in args.roles if role not in ROLES]
        if invalid_roles:
            print(f"❌ Invalid roles: {invalid_roles}")
            print("Use --list-roles to see available options")
            sys.exit(1)
    
    try:
        extractor = CountryBasedEmailExtractor()
        stats = extractor.extract_leads(
            search_roles,
            args.max_leads,
            args.delay
        )
        extractor.display_summary(stats)
        
    except KeyboardInterrupt:
        print("\n🛑 Extraction interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logging.error(f"Fatal error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 