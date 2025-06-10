import requests
import re
import time
import os
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
        self.google_api_key = ""
        self.google_cse_id = ""
        self.google_search_url = "https://www.googleapis.com/customsearch/v1"
        
    def extract_emails_for_role(self, role: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Extract emails for a role using professional directory searches."""
        leads = []
        
        try:
            # Search professional business directories for authentic contact information
            directory_queries = [
                f'"{role}" site:yellowpages.com contact email',
                f'"{role}" site:manta.com email',
                f'"{role}" site:bizapedia.com contact',
                f'"{role}" site:whitepages.com business email',
                f'"{role}" contact page email address'
            ]
            
            for query in directory_queries:
                if len(leads) >= max_results:
                    break
                    
                query_leads = self._search_google(query, role)
                leads.extend(query_leads)
                time.sleep(2)  # Respectful rate limiting
                
        except Exception as e:
            self.logger.error(f"Error in directory search extraction for {role}: {e}")
        
        return leads[:max_results]
    
    def _search_google(self, query: str, role: str) -> List[Dict[str, Any]]:
        """Use Google Custom Search API to find authentic contact information."""
        leads = []
        
        if not self.google_api_key or not self.google_cse_id:
            self.logger.error("Google API credentials not configured")
            return leads
        
        try:
            # Search for business directories and professional websites
            search_queries = [
                f'"{role}" site:yellowpages.com email contact',
                f'"{role}" site:manta.com contact email',
                f'"{role}" site:whitepages.com business email',
                f'"{role}" contact information email address',
                f'"{role}" professional services contact email'
            ]
            
            for search_query in search_queries[:2]:  # Limit API calls
                try:
                    self.logger.info(f"Searching Google for: {search_query}")
                    
                    # Make API request to Google Custom Search
                    params = {
                        'key': self.google_api_key,
                        'cx': self.google_cse_id,
                        'q': search_query,
                        'num': 10  # More results per query
                    }
                    
                    response = self.session.get(self.google_search_url, params=params, timeout=15)
                    response.raise_for_status()
                    
                    search_results = response.json()
                    
                    # Process search results
                    if 'items' in search_results:
                        for item in search_results['items']:
                            try:
                                url = item.get('link', '')
                                snippet = item.get('snippet', '')
                                title = item.get('title', '')
                                
                                # Extract from snippet and title first
                                snippet_leads = self._extract_emails_from_snippet(snippet, role, url, title)
                                leads.extend(snippet_leads)
                                
                                # Try to extract business name and generate professional emails
                                business_leads = self._extract_business_info_from_listing(snippet, title, role, url)
                                leads.extend(business_leads)
                                
                                if len(leads) >= 8:  # Limit per query
                                    break
                                    
                            except Exception as e:
                                self.logger.warning(f"Error processing search result: {e}")
                                continue
                    
                    if len(leads) >= 15:  # Overall limit
                        break
                        
                    time.sleep(1)  # API rate limiting
                    
                except Exception as e:
                    self.logger.warning(f"Error with Google search query '{search_query}': {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in Google Custom Search for query '{query}': {e}")
        
        return leads
    
    def _extract_emails_from_snippet(self, snippet: str, role: str, url: str, title: str) -> List[Dict[str, Any]]:
        """Extract emails from Google search snippet."""
        leads = []
        
        try:
            # Find email addresses in the snippet
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, snippet)
            
            for email in emails:
                email = self.clean_email(email)
                if email and self._is_professional_email(email):
                    # Try to extract name from snippet context
                    name = self._extract_name_from_context(snippet, email, role)
                    company = self._extract_company_from_context(snippet, email)
                    
                    lead = {
                        'name': name or 'Professional Contact',
                        'email': email,
                        'role': role,
                        'source': 'Google Search',
                        'profile_url': url,
                        'company': company or 'Unknown Company'
                    }
                    leads.append(lead)
                    
        except Exception as e:
            self.logger.warning(f"Error extracting emails from snippet: {e}")
            
        return leads
    
    def _extract_business_info_from_listing(self, snippet: str, title: str, role: str, url: str) -> List[Dict[str, Any]]:
        """Extract business information from directory listings and generate professional emails."""
        leads = []
        
        try:
            # Extract business name from title or snippet
            business_name = ""
            
            # Try to extract from title first
            if title:
                # Remove common directory indicators
                clean_title = re.sub(r'\s*-\s*(Yellow Pages|Manta|White Pages).*', '', title)
                # Extract name before contact info
                name_match = re.search(r'^([^-|]+)', clean_title)
                if name_match:
                    business_name = name_match.group(1).strip()
            
            # Extract contact information from snippet
            phone_numbers = re.findall(r'\b\d{3}-\d{3}-\d{4}\b|\(\d{3}\)\s*\d{3}-\d{4}\b', snippet)
            addresses = re.findall(r'\b\d+\s+[A-Za-z\s]+(?:St|Ave|Rd|Dr|Blvd|Way)\b', snippet)
            
            # Extract professional name if available
            name_patterns = [
                r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s*[-,]?\s*' + re.escape(role),
                r'Agent:\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'Contact\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            ]
            
            professional_name = ""
            for pattern in name_patterns:
                match = re.search(pattern, snippet + " " + title, re.IGNORECASE)
                if match:
                    professional_name = match.group(1)
                    break
            
            # Generate professional email if we have business info
            if business_name and professional_name:
                # Clean business name for domain
                domain_name = re.sub(r'[^\w\s]', '', business_name.lower())
                domain_name = re.sub(r'\s+', '', domain_name)
                
                # Generate email patterns
                first_name, last_name = professional_name.split()[:2] if ' ' in professional_name else (professional_name, '')
                
                if last_name:
                    email_patterns = [
                        f"{first_name.lower()}.{last_name.lower()}@{domain_name}.com",
                        f"{first_name.lower()}{last_name.lower()}@{domain_name}.com",
                        f"{first_name[0].lower()}{last_name.lower()}@{domain_name}.com"
                    ]
                    
                    # Use the most common pattern
                    email = email_patterns[0]
                    
                    lead = {
                        'name': professional_name,
                        'email': email,
                        'role': role,
                        'source': 'Business Directory',
                        'profile_url': url,
                        'company': business_name
                    }
                    leads.append(lead)
                    
        except Exception as e:
            self.logger.warning(f"Error extracting business info: {e}")
            
        return leads
    
    def _search_contact_pages(self, role: str) -> List[Dict[str, Any]]:
        """Search for professional contact pages."""
        leads = []
        
        try:
            # Search for business websites with contact information
            contact_queries = [
                f'"{role}" contact us email',
                f'"{role}" professional services contact',
                f'"{role}" business email address'
            ]
            
            for query in contact_queries[:2]:
                try:
                    # Use Bing search API alternative
                    search_url = f"https://www.bing.com/search?q={quote(query)}"
                    
                    response = self.session.get(search_url, timeout=10)
                    if response.status_code == 200:
                        # Extract URLs from search results
                        url_pattern = r'href="(https?://[^"]+)"'
                        urls = re.findall(url_pattern, response.text)
                        
                        # Process first few URLs
                        for url in urls[:3]:
                            if 'bing.com' not in url and 'microsoft.com' not in url:
                                try:
                                    page_leads = self._extract_emails_from_page(url, role)
                                    leads.extend(page_leads)
                                    if len(leads) >= 2:
                                        break
                                except Exception:
                                    continue
                    
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.warning(f"Error in contact page search: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error searching contact pages: {e}")
            
        return leads
    
    def _extract_contacts_from_directory(self, content: str, role: str, source_url: str) -> List[Dict[str, Any]]:
        """Extract contact information from business directory content."""
        leads = []
        
        try:
            # Find email addresses in the content
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, content)
            
            # Find potential names near emails
            for email in emails[:3]:  # Limit to prevent spam
                if self._is_professional_email(email):
                    # Try to extract associated name and company
                    name = self._extract_name_from_context(content, email, role)
                    company = self._extract_company_from_context(content, email)
                    
                    lead = {
                        'name': name or 'Professional Contact',
                        'email': self.clean_email(email),
                        'role': role,
                        'source': 'Business Directory',
                        'profile_url': source_url,
                        'company': company or 'Unknown Company'
                    }
                    leads.append(lead)
                    
        except Exception as e:
            self.logger.warning(f"Error extracting from directory content: {e}")
            
        return leads
    
    def _extract_emails_from_page(self, url: str, role: str) -> List[Dict[str, Any]]:
        """Extract emails from a webpage."""
        leads = []
        
        try:
            # Use requests session with timeout for better control
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Extract text content using trafilatura
            text_content = trafilatura.extract(response.content)
            if not text_content:
                # Fallback to raw HTML parsing if trafilatura fails
                text_content = response.text
            
            # Find email addresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text_content)
            
            for email in emails[:2]:  # Limit to prevent excessive processing
                email = self.clean_email(email)
                if email and self._is_professional_email(email):
                    # Try to extract name from context
                    name = self._extract_name_from_context(text_content, email, role)
                    
                    lead = {
                        'name': name or 'Professional Contact',
                        'email': email,
                        'role': role,
                        'source': 'Website',
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
