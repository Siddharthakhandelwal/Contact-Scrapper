"""
Email validation utilities.
"""

import re
import logging


class EmailValidator:
    """Validates email addresses for quality and format."""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Comprehensive email regex pattern
        self.email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Known disposable email domains
        self.disposable_domains = {
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com', 'temp-mail.org'
        }
        
        # Common invalid patterns
        self.invalid_patterns = [
            r'noreply',
            r'no-reply',
            r'donotreply',
            r'test@',
            r'example@',
            r'sample@',
            r'demo@',
            r'admin@.*\.local',
            r'postmaster@',
        ]
        
    def is_valid(self, email: str) -> bool:
        """
        Validate email address format and quality.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email is valid and appears professional
        """
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip().lower()
        
        # Basic format validation
        if not self.email_pattern.match(email):
            self.logger.debug(f"Invalid email format: {email}")
            return False
        
        # Check for invalid patterns
        for pattern in self.invalid_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                self.logger.debug(f"Email matches invalid pattern '{pattern}': {email}")
                return False
        
        # Check for disposable email domains
        domain = email.split('@')[1]
        if domain in self.disposable_domains:
            self.logger.debug(f"Disposable email domain: {email}")
            return False
        
        # Additional quality checks
        if not self._is_quality_email(email):
            return False
        
        return True
    
    def _is_quality_email(self, email: str) -> bool:
        """Additional quality checks for email addresses."""
        local_part, domain = email.split('@')
        
        # Local part should not be too short or too long
        if len(local_part) < 2 or len(local_part) > 64:
            return False
        
        # Domain should not be too short
        if len(domain) < 4:
            return False
        
        # Should not have consecutive dots
        if '..' in email:
            return False
        
        # Should not start or end with dots
        if local_part.startswith('.') or local_part.endswith('.'):
            return False
        
        # Domain should have at least one dot
        if '.' not in domain:
            return False
        
        # TLD should be at least 2 characters
        tld = domain.split('.')[-1]
        if len(tld) < 2:
            return False
        
        return True
    
    def normalize_email(self, email: str) -> str:
        """Normalize email address for consistency."""
        if not email:
            return ""
        
        return email.strip().lower()
    
    def get_domain(self, email: str) -> str:
        """Extract domain from email address."""
        if not self.is_valid(email):
            return ""
        
        return email.split('@')[1].lower()
    
    def is_corporate_email(self, email: str) -> bool:
        """Check if email appears to be from a corporate domain."""
        if not self.is_valid(email):
            return False
        
        domain = self.get_domain(email)
        
        # Common personal email domains
        personal_domains = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'protonmail.com', 'live.com'
        }
        
        return domain not in personal_domains
