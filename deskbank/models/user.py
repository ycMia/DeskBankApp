"""
User models for the banking system.
"""

import uuid
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .account import Account


class User(ABC):
    """Abstract User class representing a bank user."""
    
    def __init__(self, username: str, password: str, email: Optional[str] = None,
                 full_name: Optional[str] = None):
        """
        Initialize a new user.
        
        Args:
            username: Unique username for the user
            password: Plain text password (will be hashed)
            email: User's email address
            full_name: User's full name
        """
        self.userId = str(uuid.uuid4())
        self.username = username
        self.passwordHash = self._hash_password(password)
        self.email = email
        self.full_name = full_name or username
        self.created_at = datetime.now()
        self.last_login: Optional[datetime] = None
        self.is_active = True
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password using SHA-256 with salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        # In production, use bcrypt or similar with proper salt
        salt = self.userId[:16]  # Use part of UUID as salt
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            True if password is correct
        """
        return self.passwordHash == self._hash_password(password)
    
    def change_password(self, old_password: str, new_password: str) -> bool:
        """
        Change user's password.
        
        Args:
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password was changed successfully
            
        Raises:
            ValueError: If old password is incorrect
        """
        if not self.verify_password(old_password):
            raise ValueError("Current password is incorrect")
        
        self.passwordHash = self._hash_password(new_password)
        return True
    
    def update_last_login(self) -> None:
        """Update the last login timestamp."""
        self.last_login = datetime.now()
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
    
    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True
    
    def __str__(self) -> str:
        """String representation of the user."""
        return f"{self.__class__.__name__}: {self.username} ({self.full_name})"
    
    def __repr__(self) -> str:
        """Developer representation of the user."""
        return (f"{self.__class__.__name__}(id={self.userId[:8]}..., "
                f"username={self.username}, active={self.is_active})")
    
    def to_dict(self) -> dict:
        """Convert user to dictionary for serialization."""
        return {
            'user_id': self.userId,
            'username': self.username,
            'password_hash': self.passwordHash,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'user_type': self.__class__.__name__
        }


class Customer(User):
    """Customer class representing a bank customer with accounts."""
    
    def __init__(self, username: str, password: str, email: Optional[str] = None,
                 full_name: Optional[str] = None):
        """
        Initialize a new customer.
        
        Args:
            username: Unique username for the customer
            password: Plain text password
            email: Customer's email address
            full_name: Customer's full name
        """
        super().__init__(username, password, email, full_name)
        self._accounts: List['Account'] = []
        self.customer_since = datetime.now()
    
    def add_account(self, account: 'Account') -> None:
        """
        Add an account to the customer.
        
        Args:
            account: Account to add
        """
        account.owner_id = self.userId
        self._accounts.append(account)
    
    def remove_account(self, account_number: str) -> bool:
        """
        Remove an account from the customer.
        
        Args:
            account_number: Account number to remove
            
        Returns:
            True if account was removed
        """
        for i, account in enumerate(self._accounts):
            if account.accountNumber == account_number:
                self._accounts.pop(i)
                return True
        return False
    
    def get_accounts(self) -> List['Account']:
        """
        Get all accounts belonging to the customer.
        
        Returns:
            List of customer's accounts
        """
        return self._accounts.copy()
    
    def get_account(self, account_number: str) -> Optional['Account']:
        """
        Get a specific account by account number.
        
        Args:
            account_number: Account number to find
            
        Returns:
            Account if found, None otherwise
        """
        for account in self._accounts:
            if account.accountNumber == account_number:
                return account
        return None
    
    def get_total_balance(self) -> float:
        """
        Get total balance across all accounts.
        
        Returns:
            Total balance
        """
        return sum(account.getBalance() for account in self._accounts)
    
    def make_payment(self, account_number: str, amount: float, 
                    description: Optional[str] = None) -> 'Transaction':
        """
        Make a payment/withdrawal from a specific account.
        
        Args:
            account_number: Account to withdraw from
            amount: Amount to withdraw
            description: Optional description
            
        Returns:
            Transaction object
            
        Raises:
            ValueError: If account not found or withdrawal fails
        """
        account = self.get_account(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        return account.withdraw(amount, description)
    
    def to_dict(self) -> dict:
        """Convert customer to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            'customer_since': self.customer_since.isoformat(),
            'accounts': [account.to_dict() for account in self._accounts]
        })
        return data


class Manager(User):
    """Manager class representing a bank manager."""
    
    def __init__(self, username: str, password: str, employee_id: Optional[str] = None,
                 email: Optional[str] = None, full_name: Optional[str] = None,
                 department: Optional[str] = None):
        """
        Initialize a new manager.
        
        Args:
            username: Unique username for the manager
            password: Plain text password
            employee_id: Manager's employee ID
            email: Manager's email address
            full_name: Manager's full name
            department: Manager's department
        """
        super().__init__(username, password, email, full_name)
        self.employeeId = employee_id or f"MGR{str(uuid.uuid4())[:8].upper()}"
        self.department = department or "Banking Operations"
        self.hire_date = datetime.now()
        self.permissions = self._get_default_permissions()
    
    def _get_default_permissions(self) -> List[str]:
        """Get default permissions for a manager."""
        return [
            "view_customers",
            "add_customer",
            "remove_customer",
            "view_accounts",
            "view_transactions",
            "generate_reports",
            "system_statistics"
        ]
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if manager has a specific permission.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if manager has the permission
        """
        return permission in self.permissions
    
    def add_permission(self, permission: str) -> None:
        """
        Add a permission to the manager.
        
        Args:
            permission: Permission to add
        """
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def remove_permission(self, permission: str) -> None:
        """
        Remove a permission from the manager.
        
        Args:
            permission: Permission to remove
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def to_dict(self) -> dict:
        """Convert manager to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            'employee_id': self.employeeId,
            'department': self.department,
            'hire_date': self.hire_date.isoformat(),
            'permissions': self.permissions
        })
        return data