"""
CSV file management for email leads.
"""

import csv
import os
import logging
from typing import Dict, Any, List, Set
from datetime import datetime


class CSVManager:
    """Manages CSV file operations for email leads."""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # CSV headers
        self.headers = [
            'name', 'email', 'role', 'source', 'profile_url', 
            'company', 'date_added', 'verified'
        ]
        
        # Initialize CSV file if it doesn't exist
        self._initialize_csv()
        
        # Cache for duplicate checking
        self._email_cache = None
        
    def _initialize_csv(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file_path):
            try:
                with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=self.headers)
                    writer.writeheader()
                self.logger.info(f"Created new CSV file: {self.csv_file_path}")
            except Exception as e:
                self.logger.error(f"Error creating CSV file: {e}")
                raise
    
    def add_lead(self, lead: Dict[str, Any]) -> bool:
        """
        Add a new lead to the CSV file.
        
        Args:
            lead: Dictionary containing lead information
            
        Returns:
            True if lead was added successfully, False otherwise
        """
        try:
            # Prepare lead data
            lead_data = {
                'name': lead.get('name', ''),
                'email': lead.get('email', ''),
                'role': lead.get('role', ''),
                'source': lead.get('source', ''),
                'profile_url': lead.get('profile_url', ''),
                'company': lead.get('company', ''),
                'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'verified': 'No'
            }
            
            # Validate required fields
            if not lead_data['email']:
                self.logger.warning("Attempted to add lead without email")
                return False
            
            # Write to CSV
            with open(self.csv_file_path, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.headers)
                writer.writerow(lead_data)
            
            # Update cache
            if self._email_cache is not None:
                self._email_cache.add(lead_data['email'].lower())
            
            self.logger.info(f"Added lead: {lead_data['email']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding lead to CSV: {e}")
            return False
    
    def is_duplicate(self, email: str) -> bool:
        """
        Check if email already exists in the CSV file.
        
        Args:
            email: Email address to check
            
        Returns:
            True if email already exists, False otherwise
        """
        if not email:
            return False
        
        email = email.lower().strip()
        
        # Use cache if available
        if self._email_cache is None:
            self._load_email_cache()
        
        return email in self._email_cache
    
    def _load_email_cache(self):
        """Load all existing emails into memory for fast duplicate checking."""
        self._email_cache = set()
        
        try:
            if os.path.exists(self.csv_file_path):
                with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        email = row.get('email', '').lower().strip()
                        if email:
                            self._email_cache.add(email)
                            
                self.logger.info(f"Loaded {len(self._email_cache)} existing emails into cache")
        except Exception as e:
            self.logger.error(f"Error loading email cache: {e}")
            self._email_cache = set()
    
    def get_all_leads(self) -> List[Dict[str, Any]]:
        """
        Get all leads from the CSV file.
        
        Returns:
            List of lead dictionaries
        """
        leads = []
        
        try:
            if os.path.exists(self.csv_file_path):
                with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    leads = list(reader)
        except Exception as e:
            self.logger.error(f"Error reading leads from CSV: {e}")
        
        return leads
    
    def get_leads_by_role(self, role: str) -> List[Dict[str, Any]]:
        """
        Get all leads for a specific role.
        
        Args:
            role: Professional role to filter by
            
        Returns:
            List of lead dictionaries for the specified role
        """
        all_leads = self.get_all_leads()
        return [lead for lead in all_leads if lead.get('role', '').lower() == role.lower()]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the leads database.
        
        Returns:
            Dictionary containing various statistics
        """
        leads = self.get_all_leads()
        
        if not leads:
            return {
                'total_leads': 0,
                'unique_roles': 0,
                'unique_companies': 0,
                'sources': {},
                'recent_additions': 0
            }
        
        # Calculate statistics
        roles = set()
        companies = set()
        sources = {}
        recent_count = 0
        
        # Get today's date for recent additions
        today = datetime.now().date()
        
        for lead in leads:
            # Roles
            role = lead.get('role', '').strip()
            if role:
                roles.add(role)
            
            # Companies
            company = lead.get('company', '').strip()
            if company:
                companies.add(company)
            
            # Sources
            source = lead.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
            
            # Recent additions (today)
            try:
                date_added = datetime.strptime(lead.get('date_added', ''), '%Y-%m-%d %H:%M:%S').date()
                if date_added == today:
                    recent_count += 1
            except ValueError:
                pass
        
        return {
            'total_leads': len(leads),
            'unique_roles': len(roles),
            'unique_companies': len(companies),
            'sources': sources,
            'recent_additions': recent_count
        }
    
    def backup_csv(self) -> str:
        """
        Create a backup of the current CSV file.
        
        Returns:
            Path to the backup file
        """
        if not os.path.exists(self.csv_file_path):
            return ""
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{self.csv_file_path}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(self.csv_file_path, backup_path)
            self.logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return ""
