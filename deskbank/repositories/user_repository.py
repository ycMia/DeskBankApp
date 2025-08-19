"""
User repository for managing user data.
"""

from typing import List, Optional
from ..models.user import User, Customer, Manager
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for managing users."""
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize the user repository.
        
        Args:
            data_file: Optional file path for data persistence
        """
        super().__init__(data_file)
    
    def _serialize_item(self, user: User) -> dict:
        """Serialize a user to dictionary."""
        return user.to_dict()
    
    def _deserialize_item(self, data: dict) -> User:
        """Deserialize dictionary data to user."""
        user_type = data.get('user_type', 'Customer')
        
        if user_type == 'Manager':
            manager = Manager.__new__(Manager)
            manager.userId = data['user_id']
            manager.username = data['username']
            manager.passwordHash = data['password_hash']
            manager.email = data.get('email')
            manager.full_name = data.get('full_name', data['username'])
            manager.is_active = data.get('is_active', True)
            manager.employeeId = data.get('employee_id', f"MGR{manager.userId[:8]}")
            manager.department = data.get('department', 'Banking Operations')
            manager.permissions = data.get('permissions', manager._get_default_permissions())
            
            # Parse dates
            from datetime import datetime
            manager.created_at = datetime.fromisoformat(data['created_at'])
            manager.last_login = (datetime.fromisoformat(data['last_login']) 
                                if data.get('last_login') else None)
            manager.hire_date = (datetime.fromisoformat(data['hire_date'])
                               if data.get('hire_date') else manager.created_at)
            
            return manager
        else:
            customer = Customer.__new__(Customer)
            customer.userId = data['user_id']
            customer.username = data['username']
            customer.passwordHash = data['password_hash']
            customer.email = data.get('email')
            customer.full_name = data.get('full_name', data['username'])
            customer.is_active = data.get('is_active', True)
            customer._accounts = []  # Accounts are managed separately
            
            # Parse dates
            from datetime import datetime
            customer.created_at = datetime.fromisoformat(data['created_at'])
            customer.last_login = (datetime.fromisoformat(data['last_login']) 
                                 if data.get('last_login') else None)
            customer.customer_since = (datetime.fromisoformat(data['customer_since'])
                                     if data.get('customer_since') else customer.created_at)
            
            return customer
    
    def _get_item_id(self, user: User) -> str:
        """Get unique identifier for a user."""
        return user.userId
    
    def find_by_username(self, username: str) -> Optional[User]:
        """
        Find a user by username.
        
        Args:
            username: Username to search for
            
        Returns:
            User if found, None otherwise
        """
        for user in self._data.values():
            if user.username == username:
                return user
        return None
    
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email.
        
        Args:
            email: Email to search for
            
        Returns:
            User if found, None otherwise
        """
        for user in self._data.values():
            if user.email == email:
                return user
        return None
    
    def get_customers(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List of all customers
        """
        return [user for user in self._data.values() if isinstance(user, Customer)]
    
    def get_managers(self) -> List[Manager]:
        """
        Get all managers.
        
        Returns:
            List of all managers
        """
        return [user for user in self._data.values() if isinstance(user, Manager)]
    
    def get_active_users(self) -> List[User]:
        """
        Get all active users.
        
        Returns:
            List of active users
        """
        return [user for user in self._data.values() if user.is_active]
    
    def username_exists(self, username: str) -> bool:
        """
        Check if a username already exists.
        
        Args:
            username: Username to check
            
        Returns:
            True if username exists
        """
        return self.find_by_username(username) is not None
    
    def email_exists(self, email: str) -> bool:
        """
        Check if an email already exists.
        
        Args:
            email: Email to check
            
        Returns:
            True if email exists
        """
        return email is not None and self.find_by_email(email) is not None
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = self.find_by_username(username)
        if user and user.is_active and user.verify_password(password):
            user.update_last_login()
            self.update(user)  # Save the updated last_login
            return user
        return None
    
    def create_customer(self, username: str, password: str, 
                       email: Optional[str] = None, 
                       full_name: Optional[str] = None) -> Customer:
        """
        Create a new customer.
        
        Args:
            username: Unique username
            password: Password
            email: Optional email
            full_name: Optional full name
            
        Returns:
            Created customer
            
        Raises:
            ValueError: If username already exists
        """
        if self.username_exists(username):
            raise ValueError(f"Username '{username}' already exists")
        
        if email and self.email_exists(email):
            raise ValueError(f"Email '{email}' already exists")
        
        customer = Customer(username, password, email, full_name)
        self.add(customer)
        return customer
    
    def create_manager(self, username: str, password: str,
                      employee_id: Optional[str] = None,
                      email: Optional[str] = None,
                      full_name: Optional[str] = None,
                      department: Optional[str] = None) -> Manager:
        """
        Create a new manager.
        
        Args:
            username: Unique username
            password: Password
            employee_id: Optional employee ID
            email: Optional email
            full_name: Optional full name
            department: Optional department
            
        Returns:
            Created manager
            
        Raises:
            ValueError: If username already exists
        """
        if self.username_exists(username):
            raise ValueError(f"Username '{username}' already exists")
        
        if email and self.email_exists(email):
            raise ValueError(f"Email '{email}' already exists")
        
        manager = Manager(username, password, employee_id, email, full_name, department)
        self.add(manager)
        return manager