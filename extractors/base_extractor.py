"""
Base extractor class for email lead extraction.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging


class BaseExtractor(ABC):
    """Abstract base class for email extractors."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def extract_emails_for_role(self, role: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Extract email leads for a specific role.
        
        Args:
            role: Professional role to search for
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing lead information:
            [
                {
                    'name': 'John Doe',
                    'email': 'john@example.com',
                    'role': 'Real Estate Agent',
                    'source': 'Google Search',
                    'profile_url': 'https://...',
                    'company': 'ABC Realty'
                }
            ]
        """
        pass
    
    def clean_email(self, email: str) -> str:
        """Clean and normalize email address."""
        if not email:
            return ""
        return email.strip().lower()
    
    def clean_name(self, name: str) -> str:
        """Clean and normalize name."""
        if not name:
            return ""
        return " ".join(name.strip().split())
