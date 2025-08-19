"""
Validation utilities for DeskBank application.
"""

import re
from typing import Tuple, Optional
from decimal import Decimal, InvalidOperation


class Validators:
    """Collection of validation utilities."""
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, str]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not username:
            return False, "Username cannot be empty"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 50:
            return False, "Username cannot be longer than 50 characters"
        
        # Allow alphanumeric characters, underscores, and hyphens
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            return False, "Username can only contain letters, numbers, underscores, and hyphens"
        
        # Must start with a letter
        if not username[0].isalpha():
            return False, "Username must start with a letter"
        
        return True, "Username is valid"
    
    @staticmethod
    def validate_password(password: str, min_length: int = 8,
                         require_uppercase: bool = True,
                         require_lowercase: bool = True,
                         require_numbers: bool = True,
                         require_special: bool = True) -> Tuple[bool, str]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            min_length: Minimum password length
            require_uppercase: Require uppercase letters
            require_lowercase: Require lowercase letters
            require_numbers: Require numbers
            require_special: Require special characters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        
        if len(password) > 128:
            return False, "Password cannot be longer than 128 characters"
        
        if require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if require_numbers and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if require_special:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False, "Password must contain at least one special character"
        
        # Check for common weak passwords
        weak_patterns = [
            r'(.)\1{3,}',  # Repeated characters (aaaa)
            r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                return False, "Password contains weak patterns (repeated or sequential characters)"
        
        return True, "Password is strong"
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not email:
            return True, "Email is optional"  # Email is optional
        
        if len(email) > 254:
            return False, "Email address is too long"
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        # Check for valid domain
        if '..' in email:
            return False, "Email contains consecutive dots"
        
        return True, "Email is valid"
    
    @staticmethod
    def validate_amount(amount: str) -> Tuple[bool, str, Optional[float]]:
        """
        Validate monetary amount.
        
        Args:
            amount: Amount string to validate
            
        Returns:
            Tuple of (is_valid, error_message, parsed_amount)
        """
        if not amount:
            return False, "Amount cannot be empty", None
        
        try:
            # Remove common formatting characters
            cleaned_amount = amount.replace(',', '').replace('$', '').strip()
            
            # Convert to decimal for precise validation
            decimal_amount = Decimal(cleaned_amount)
            
            if decimal_amount < 0:
                return False, "Amount cannot be negative", None
            
            if decimal_amount == 0:
                return False, "Amount must be greater than zero", None
            
            # Check for reasonable maximum (1 billion)
            if decimal_amount > Decimal('1000000000'):
                return False, "Amount is too large", None
            
            # Check decimal places (max 2)
            if decimal_amount.as_tuple().exponent < -2:
                return False, "Amount cannot have more than 2 decimal places", None
            
            return True, "Amount is valid", float(decimal_amount)
        
        except (InvalidOperation, ValueError):
            return False, "Invalid amount format", None
    
    @staticmethod
    def validate_account_type(account_type: str) -> Tuple[bool, str]:
        """
        Validate account type.
        
        Args:
            account_type: Account type to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        valid_types = ["Savings", "Checking", "Business"]
        
        if not account_type:
            return False, "Account type cannot be empty"
        
        if account_type not in valid_types:
            return False, f"Invalid account type. Must be one of: {', '.join(valid_types)}"
        
        return True, "Account type is valid"
    
    @staticmethod
    def validate_full_name(full_name: str) -> Tuple[bool, str]:
        """
        Validate full name format.
        
        Args:
            full_name: Full name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not full_name:
            return True, "Full name is optional"  # Full name is optional
        
        if len(full_name) < 2:
            return False, "Full name must be at least 2 characters long"
        
        if len(full_name) > 100:
            return False, "Full name cannot be longer than 100 characters"
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", full_name):
            return False, "Full name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Check for reasonable format (at least one space or reasonable single name)
        if ' ' not in full_name and len(full_name) < 2:
            return False, "Please enter a valid full name"
        
        return True, "Full name is valid"
    
    @staticmethod
    def validate_account_number(account_number: str) -> Tuple[bool, str]:
        """
        Validate account number format.
        
        Args:
            account_number: Account number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not account_number:
            return False, "Account number cannot be empty"
        
        if len(account_number) != 8:
            return False, "Account number must be exactly 8 characters"
        
        if not account_number.isupper():
            return False, "Account number must be uppercase"
        
        # Check if it's alphanumeric
        if not account_number.isalnum():
            return False, "Account number must be alphanumeric"
        
        return True, "Account number is valid"
    
    @staticmethod
    def validate_employee_id(employee_id: str) -> Tuple[bool, str]:
        """
        Validate employee ID format.
        
        Args:
            employee_id: Employee ID to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not employee_id:
            return False, "Employee ID cannot be empty"
        
        if len(employee_id) < 3 or len(employee_id) > 20:
            return False, "Employee ID must be between 3 and 20 characters"
        
        # Allow alphanumeric characters and hyphens
        if not re.match(r'^[a-zA-Z0-9-]+$', employee_id):
            return False, "Employee ID can only contain letters, numbers, and hyphens"
        
        return True, "Employee ID is valid"
    
    @staticmethod
    def validate_transaction_description(description: str) -> Tuple[bool, str]:
        """
        Validate transaction description.
        
        Args:
            description: Description to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not description:
            return True, "Description is optional"  # Description is optional
        
        if len(description) > 500:
            return False, "Description cannot be longer than 500 characters"
        
        # Remove excessive whitespace and check for meaningful content
        cleaned_desc = ' '.join(description.split())
        if len(cleaned_desc) < 3:
            return False, "Description must be at least 3 characters long"
        
        # Check for inappropriate characters (basic check)
        if any(ord(char) < 32 for char in description if char not in '\t\n\r'):
            return False, "Description contains invalid characters"
        
        return True, "Description is valid"
    
    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return True, "Phone number is optional"
        
        # Remove formatting characters
        cleaned_phone = re.sub(r'[^\d]', '', phone)
        
        if len(cleaned_phone) < 10:
            return False, "Phone number must have at least 10 digits"
        
        if len(cleaned_phone) > 15:
            return False, "Phone number cannot have more than 15 digits"
        
        # Check for valid phone pattern (basic)
        if not re.match(r'^\+?[\d\s\-\(\)\.]{10,}$', phone):
            return False, "Invalid phone number format"
        
        return True, "Phone number is valid"