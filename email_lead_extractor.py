#!/usr/bin/env python3
"""
Professional Email Lead Extractor
A command-line tool for extracting and managing professional email leads based on specific roles.
"""

import argparse
import sys
import time
from typing import List, Dict, Any
import logging

from config import ROLES, CSV_FILE_PATH, LOG_FILE_PATH
from utils.logger import setup_logger
from utils.csv_manager import CSVManager
from utils.email_validator import EmailValidator
from extractors.google_search_extractor import GoogleSearchExtractor
from extractors.linkedin_extractor import LinkedInExtractor


class EmailLeadExtractor:
    """Main class for orchestrating email lead extraction."""
    
    def __init__(self):
        self.logger = setup_logger('email_lead_extractor', LOG_FILE_PATH)
        self.csv_manager = CSVManager(CSV_FILE_PATH)
        self.email_validator = EmailValidator()
        self.extractors = [
            GoogleSearchExtractor(),
            LinkedInExtractor()
        ]
        
    def extract_leads(self, roles: List[str], max_leads_per_role: int = 10, 
                     delay_between_searches: float = 2.0) -> Dict[str, Any]:
        """
        Extract email leads for specified roles.
        
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
            'errors': 0
        }
        
        self.logger.info(f"Starting lead extraction for {len(roles)} roles")
        print(f"🚀 Starting email lead extraction for {len(roles)} roles...")
        
        for i, role in enumerate(roles, 1):
            print(f"\n[{i}/{len(roles)}] Searching for: {role}")
            self.logger.info(f"Searching for role: {role}")
            
            try:
                role_leads = []
                
                # Try each extractor
                for extractor in self.extractors:
                    try:
                        extractor_leads = extractor.extract_emails_for_role(
                            role, max_leads_per_role
                        )
                        role_leads.extend(extractor_leads)
                        
                        if len(role_leads) >= max_leads_per_role:
                            break
                            
                    except Exception as e:
                        self.logger.error(f"Extractor {extractor.__class__.__name__} failed for role {role}: {e}")
                        stats['errors'] += 1
                        continue
                
                # Process found leads
                for lead in role_leads[:max_leads_per_role]:
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
                    
                    # Save new lead
                    if self.csv_manager.add_lead(lead):
                        stats['new_leads_found'] += 1
                        self.logger.info(f"New lead added: {lead['email']}")
                        print(f"  ✅ New lead: {lead['email']} ({lead.get('name', 'Unknown')})")
                    else:
                        stats['errors'] += 1
                
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
        print(f"Errors encountered: {stats['errors']}")
        print(f"\n💾 Data saved to: {CSV_FILE_PATH}")
        print(f"📝 Logs saved to: {LOG_FILE_PATH}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Extract professional email leads based on specific roles"
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
        extractor = EmailLeadExtractor()
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
