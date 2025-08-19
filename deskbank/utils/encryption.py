"""
Encryption utilities for DeskBank application.
"""

import hashlib
import secrets
import base64
from typing import Optional, Tuple


class EncryptionUtil:
    """Encryption and security utilities."""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        Hash password with salt using SHA-256.
        
        Args:
            password: Plain text password
            salt: Optional salt (will generate if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Combine password and salt
        salted_password = password + salt
        
        # Hash using SHA-256
        hashed = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
        
        return hashed, salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored hashed password
            salt: Salt used for hashing
            
        Returns:
            True if password is correct
        """
        # Hash the provided password with the same salt
        test_hash, _ = EncryptionUtil.hash_password(password, salt)
        
        # Compare hashes
        return secrets.compare_digest(test_hash, hashed_password)
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a secure random token.
        
        Args:
            length: Length of token in bytes
            
        Returns:
            URL-safe base64 encoded token
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a secure session ID.
        
        Returns:
            Session ID string
        """
        return EncryptionUtil.generate_secure_token(32)
    
    @staticmethod
    def generate_account_number() -> str:
        """
        Generate a secure account number.
        
        Returns:
            8-character uppercase alphanumeric account number
        """
        # Generate random bytes and convert to uppercase alphanumeric
        token = secrets.token_hex(4).upper()
        return token
    
    @staticmethod
    def generate_employee_id(prefix: str = "EMP") -> str:
        """
        Generate employee ID.
        
        Args:
            prefix: Prefix for employee ID
            
        Returns:
            Employee ID string
        """
        random_part = secrets.token_hex(4).upper()
        return f"{prefix}{random_part}"
    
    @staticmethod
    def simple_encrypt(data: str, key: str) -> str:
        """
        Simple XOR encryption (for demonstration purposes only).
        Note: This is NOT secure for production use.
        
        Args:
            data: Data to encrypt
            key: Encryption key
            
        Returns:
            Base64 encoded encrypted data
        """
        # Extend key to match data length
        extended_key = (key * (len(data) // len(key) + 1))[:len(data)]
        
        # XOR encryption
        encrypted_bytes = bytes(a ^ b for a, b in zip(data.encode(), extended_key.encode()))
        
        # Base64 encode
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    @staticmethod
    def simple_decrypt(encrypted_data: str, key: str) -> str:
        """
        Simple XOR decryption (for demonstration purposes only).
        Note: This is NOT secure for production use.
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            key: Decryption key
            
        Returns:
            Decrypted data
        """
        try:
            # Base64 decode
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extend key to match data length
            extended_key = (key * (len(encrypted_bytes) // len(key) + 1))[:len(encrypted_bytes)]
            
            # XOR decryption
            decrypted_bytes = bytes(a ^ b for a, b in zip(encrypted_bytes, extended_key.encode()))
            
            return decrypted_bytes.decode('utf-8')
        except Exception:
            return ""
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", 
                           show_first: int = 2, show_last: int = 2) -> str:
        """
        Mask sensitive data for display.
        
        Args:
            data: Data to mask
            mask_char: Character to use for masking
            show_first: Number of characters to show at the beginning
            show_last: Number of characters to show at the end
            
        Returns:
            Masked data string
        """
        if not data or len(data) <= show_first + show_last:
            return mask_char * len(data) if data else ""
        
        first_part = data[:show_first]
        last_part = data[-show_last:] if show_last > 0 else ""
        mask_length = len(data) - show_first - show_last
        
        return first_part + mask_char * mask_length + last_part
    
    @staticmethod
    def generate_checksum(data: str) -> str:
        """
        Generate MD5 checksum for data integrity.
        
        Args:
            data: Data to generate checksum for
            
        Returns:
            MD5 checksum string
        """
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def verify_checksum(data: str, checksum: str) -> bool:
        """
        Verify data integrity using checksum.
        
        Args:
            data: Data to verify
            checksum: Expected checksum
            
        Returns:
            True if checksum matches
        """
        calculated_checksum = EncryptionUtil.generate_checksum(data)
        return secrets.compare_digest(calculated_checksum, checksum)
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """
        Generate API key.
        
        Args:
            length: Length of the key
            
        Returns:
            API key string
        """
        return f"dk_{''.join(secrets.choice('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(length))}"
    
    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """
        Constant time string comparison to prevent timing attacks.
        
        Args:
            a: First string
            b: Second string
            
        Returns:
            True if strings are equal
        """
        return secrets.compare_digest(a, b)
    
    @staticmethod
    def sanitize_input(input_string: str) -> str:
        """
        Sanitize input string by removing potentially dangerous characters.
        
        Args:
            input_string: Input to sanitize
            
        Returns:
            Sanitized string
        """
        if not input_string:
            return ""
        
        # Remove null bytes and control characters (except newline, tab, carriage return)
        sanitized = ''.join(char for char in input_string 
                          if ord(char) >= 32 or char in '\n\t\r')
        
        # Limit length to prevent buffer overflow attacks
        max_length = 1000
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """
        Generate one-time password (OTP).
        
        Args:
            length: Length of OTP
            
        Returns:
            Numeric OTP string
        """
        return ''.join(secrets.choice('0123456789') for _ in range(length))