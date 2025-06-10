"""
LinkedIn-based email extractor.
Note: This is a simplified implementation. In production, you should use LinkedIn's official APIs.
"""

import requests
import re
import time
from typing import List, Dict, Any
from urllib.parse import quote
import trafilatura

from .base_extractor import BaseExtractor


class LinkedInExtractor(BaseExtractor):
    """Extract emails from LinkedIn profiles and company pages."""
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def extract_emails_for_role(self, role: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Extract emails for a role from LinkedIn."""
        leads = []
        
        try:
            # Search for LinkedIn profiles
            search_query = f'site:linkedin.com/in "{role}"'
            
            # Use Google to find LinkedIn profiles
            search_url = f"https://www.google.com/search?q={quote(search_query)}&num=20"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            # Extract LinkedIn profile URLs
            linkedin_urls = re.findall(
                r'href="(https://[^"]*linkedin\.com/in/[^"]*)"', 
                response.text
            )
            
            # Process each profile
            for url in linkedin_urls[:max_results]:
                try:
                    profile_leads = self._extract_from_linkedin_profile(url, role)
                    leads.extend(profile_leads)
                    time.sleep(2)  # Rate limiting for LinkedIn
                    
                    if len(leads) >= max_results:
                        break
                        
                except Exception as e:
                    self.logger.warning(f"Error processing LinkedIn profile {url}: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error in LinkedIn extraction for {role}: {e}")
        
        return leads[:max_results]
    
    def _extract_from_linkedin_profile(self, url: str, role: str) -> List[Dict[str, Any]]:
        """Extract information from a LinkedIn profile."""
        leads = []
        
        try:
            # Clean the URL
            clean_url = url.split('?')[0]  # Remove query parameters
            
            # Fetch profile content
            downloaded = trafilatura.fetch_url(clean_url)
            if not downloaded:
                return leads
                
            text_content = trafilatura.extract(downloaded)
            if not text_content:
                return leads
            
            # Extract profile information
            profile_info = self._parse_linkedin_profile(text_content, clean_url, role)
            
            if profile_info:
                leads.append(profile_info)
                
        except Exception as e:
            self.logger.warning(f"Error extracting from LinkedIn profile {url}: {e}")
        
        return leads
    
    def _parse_linkedin_profile(self, text: str, url: str, role: str) -> Dict[str, Any]:
        """Parse LinkedIn profile text to extract relevant information."""
        try:
            # Extract name (first line usually contains the name)
            lines = text.split('\n')
            name = ""
            
            for line in lines:
                line = line.strip()
                if line and len(line.split()) <= 4 and any(c.isupper() for c in line):
                    # Likely a name
                    name = self.clean_name(line)
                    break
            
            # Extract current company/position
            company = ""
            current_position = ""
            
            # Look for patterns that indicate current role
            role_patterns = [
                r'at\s+([A-Z][^,.\n]+)',
                r'([A-Z][^,.\n]+)\s*•',
                r'([A-Z][^,.\n]+)\s*\|',
            ]
            
            for pattern in role_patterns:
                match = re.search(pattern, text)
                if match:
                    company = match.group(1).strip()
                    break
            
            # Generate professional email based on LinkedIn info
            email = self._generate_professional_email(name, company, url)
            
            if name and email:
                return {
                    'name': name,
                    'email': email,
                    'role': role,
                    'source': 'LinkedIn',
                    'profile_url': url,
                    'company': company
                }
                
        except Exception as e:
            self.logger.warning(f"Error parsing LinkedIn profile: {e}")
        
        return None
    
    def _generate_professional_email(self, name: str, company: str, linkedin_url: str) -> str:
        """Generate likely professional email addresses based on name and company."""
        if not name:
            return ""
        
        # Extract first and last name
        name_parts = name.split()
        if len(name_parts) < 2:
            return ""
        
        first_name = name_parts[0].lower()
        last_name = name_parts[-1].lower()
        
        # If we have company info, try to generate company email
        if company:
            # Clean company name
            company_clean = re.sub(r'[^\w\s]', '', company).strip()
            company_words = company_clean.split()
            
            if company_words:
                # Generate possible domain variations
                possible_domains = [
                    f"{company_words[0].lower()}.com",
                    f"{''.join(company_words).lower()}.com",
                ]
                
                # Generate email patterns
                email_patterns = [
                    f"{first_name}.{last_name}",
                    f"{first_name}{last_name}",
                    f"{first_name[0]}{last_name}",
                    f"{first_name}.{last_name[0]}",
                ]
                
                # Return the most likely email format
                for domain in possible_domains:
                    for pattern in email_patterns:
                        email = f"{pattern}@{domain}"
                        return email
        
        # If no company, extract from LinkedIn URL
        try:
            # Extract username from LinkedIn URL
            username_match = re.search(r'/in/([^/?]+)', linkedin_url)
            if username_match:
                username = username_match.group(1)
                # This is a fallback - in reality, you'd need other methods
                # to find actual email addresses
                return f"{username}@example.com"  # Placeholder
        except Exception:
            pass
        
        return ""
