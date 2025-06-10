"""
Google Search-based email extractor.
"""

import requests
import re
import time
from typing import List, Dict, Any
from urllib.parse import quote
import trafilatura

from .base_extractor import BaseExtractor


class GoogleSearchExtractor(BaseExtractor):
    """Extract emails using Google search results."""
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_emails_for_role(self, role: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Extract emails for a role using Google search."""
        leads = []
        
        try:
            # Search for contact pages and directories
            search_queries = [
                f'"{role}" email contact',
                f'"{role}" site:linkedin.com',
                f'"{role}" contact information',
                f'"{role}" directory email'
            ]
            
            for query in search_queries:
                if len(leads) >= max_results:
                    break
                    
                query_leads = self._search_google(query, role)
                leads.extend(query_leads)
                time.sleep(1)  # Rate limiting
                
        except Exception as e:
            self.logger.error(f"Error in Google search extraction for {role}: {e}")
        
        return leads[:max_results]
    
    def _search_google(self, query: str, role: str) -> List[Dict[str, Any]]:
        """Perform Google search and extract emails from results."""
        leads = []
        
        try:
            # Use a public search API or scrape Google results
            # Note: In production, you should use Google Custom Search API
            search_url = f"https://www.google.com/search?q={quote(query)}&num=10"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            # Extract URLs from search results
            urls = re.findall(r'href="(https?://[^"]+)"', response.text)
            
            # Filter and process URLs
            for url in urls[:5]:  # Limit to first 5 URLs
                try:
                    if 'google.com' in url or 'youtube.com' in url:
                        continue
                        
                    page_leads = self._extract_emails_from_page(url, role)
                    leads.extend(page_leads)
                    
                    if len(leads) >= 5:  # Limit per query
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Error processing URL {url}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in Google search for query '{query}': {e}")
        
        return leads
    
    def _extract_emails_from_page(self, url: str, role: str) -> List[Dict[str, Any]]:
        """Extract emails from a webpage."""
        leads = []
        
        try:
            # Fetch and extract text content
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return leads
                
            text_content = trafilatura.extract(downloaded)
            if not text_content:
                return leads
            
            # Find email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text_content)
            
            for email in emails:
                email = self.clean_email(email)
                if email and self._is_professional_email(email):
                    # Try to extract name from context
                    name = self._extract_name_from_context(text_content, email, role)
                    
                    lead = {
                        'name': name or 'Unknown',
                        'email': email,
                        'role': role,
                        'source': 'Google Search',
                        'profile_url': url,
                        'company': self._extract_company_from_context(text_content, email)
                    }
                    leads.append(lead)
                    
        except Exception as e:
            self.logger.warning(f"Error extracting emails from {url}: {e}")
        
        return leads
    
    def _is_professional_email(self, email: str) -> bool:
        """Check if email appears to be professional."""
        # Skip common personal email domains
        personal_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
        domain = email.split('@')[-1].lower()
        
        # Skip if it's a known personal domain
        if domain in personal_domains:
            return False
            
        # Skip if it contains common spam indicators
        spam_indicators = ['noreply', 'no-reply', 'donotreply', 'admin', 'info@']
        if any(indicator in email.lower() for indicator in spam_indicators):
            return False
            
        return True
    
    def _extract_name_from_context(self, text: str, email: str, role: str) -> str:
        """Try to extract name from text context around email."""
        try:
            # Look for patterns like "Contact John Doe at john@example.com"
            email_index = text.lower().find(email.lower())
            if email_index == -1:
                return ""
            
            # Get text around the email
            start = max(0, email_index - 100)
            end = min(len(text), email_index + 100)
            context = text[start:end]
            
            # Look for name patterns
            name_patterns = [
                r'contact\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[@:]',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+).*' + re.escape(email),
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, context, re.IGNORECASE)
                if match:
                    return self.clean_name(match.group(1))
                    
        except Exception:
            pass
            
        return ""
    
    def _extract_company_from_context(self, text: str, email: str) -> str:
        """Try to extract company name from email domain or context."""
        try:
            domain = email.split('@')[-1]
            # Remove common TLDs and return domain as company name
            company = domain.split('.')[0]
            return company.title()
        except Exception:
            return ""
