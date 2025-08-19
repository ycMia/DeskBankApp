"""
User service for managing users and customer operations.
"""

from typing import List, Optional
from ..models.user import User, Customer, Manager
from ..repositories.user_repository import UserRepository
from ..repositories.account_repository import AccountRepository


class UserService:
    """Service for managing users and customer operations."""
    
    def __init__(self, user_repository: UserRepository, 
                 account_repository: AccountRepository):
        """
        Initialize the user service.
        
        Args:
            user_repository: Repository for user data
            account_repository: Repository for account data
        """
        self.user_repository = user_repository
        self.account_repository = account_repository
    
    def register_customer(self, username: str, password: str,
                         email: Optional[str] = None,
                         full_name: Optional[str] = None) -> Customer:
        """
        Register a new customer.
        
        Args:
            username: Unique username
            password: Password
            email: Optional email
            full_name: Optional full name
            
        Returns:
            Created customer
            
        Raises:
            ValueError: If username or email already exists
        """
        return self.user_repository.create_customer(username, password, email, full_name)
    
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
            ValueError: If username or email already exists
        """
        return self.user_repository.create_manager(
            username, password, employee_id, email, full_name, department
        )
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get a user by their ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by their username.
        
        Args:
            username: Username
            
        Returns:
            User if found, None otherwise
        """
        return self.user_repository.find_by_username(username)
    
    def get_all_customers(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List of all customers
        """
        return self.user_repository.get_customers()
    
    def get_all_managers(self) -> List[Manager]:
        """
        Get all managers.
        
        Returns:
            List of all managers
        """
        return self.user_repository.get_managers()
    
    def get_active_users(self) -> List[User]:
        """
        Get all active users.
        
        Returns:
            List of active users
        """
        return self.user_repository.get_active_users()
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            True if user was deactivated
        """
        user = self.user_repository.get_by_id(user_id)
        if user:
            user.deactivate()
            self.user_repository.update(user)
            return True
        return False
    
    def activate_user(self, user_id: str) -> bool:
        """
        Activate a user account.
        
        Args:
            user_id: User ID to activate
            
        Returns:
            True if user was activated
        """
        user = self.user_repository.get_by_id(user_id)
        if user:
            user.activate()
            self.user_repository.update(user)
            return True
        return False
    
    def delete_customer(self, customer_id: str) -> bool:
        """
        Delete a customer and all their accounts.
        
        Args:
            customer_id: Customer ID to delete
            
        Returns:
            True if customer was deleted
            
        Raises:
            ValueError: If customer has accounts with non-zero balances
        """
        customer = self.user_repository.get_by_id(customer_id)
        if not customer or not isinstance(customer, Customer):
            return False
        
        # Check if customer has any accounts with non-zero balances
        customer_accounts = self.account_repository.find_by_owner(customer_id)
        for account in customer_accounts:
            if account.getBalance() != 0:
                raise ValueError(
                    f"Cannot delete customer with non-zero account balance: "
                    f"Account {account.accountNumber} has ${account.getBalance()}"
                )
        
        # Delete all customer accounts
        for account in customer_accounts:
            self.account_repository.delete(account.accountNumber)
        
        # Delete customer
        return self.user_repository.delete(customer_id)
    
    def change_user_password(self, user_id: str, old_password: str, 
                           new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password was changed
            
        Raises:
            ValueError: If user not found or old password is incorrect
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        success = user.change_password(old_password, new_password)
        if success:
            self.user_repository.update(user)
        
        return success
    
    def update_user_profile(self, user_id: str, email: Optional[str] = None,
                           full_name: Optional[str] = None) -> bool:
        """
        Update a user's profile information.
        
        Args:
            user_id: User ID
            email: New email (optional)
            full_name: New full name (optional)
            
        Returns:
            True if profile was updated
            
        Raises:
            ValueError: If user not found or email already exists
        """
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if email is already in use by another user
        if email and email != user.email:
            existing_user = self.user_repository.find_by_email(email)
            if existing_user and existing_user.userId != user_id:
                raise ValueError(f"Email '{email}' is already in use")
        
        # Update profile
        if email is not None:
            user.email = email
        if full_name is not None:
            user.full_name = full_name
        
        self.user_repository.update(user)
        return True
    
    def get_customer_summary(self, customer_id: str) -> dict:
        """
        Get a summary of customer information and accounts.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Dictionary with customer summary
            
        Raises:
            ValueError: If customer not found
        """
        customer = self.user_repository.get_by_id(customer_id)
        if not customer or not isinstance(customer, Customer):
            raise ValueError("Customer not found")
        
        accounts = self.account_repository.find_by_owner(customer_id)
        total_balance = sum(account.getBalance() for account in accounts)
        active_accounts = len([acc for acc in accounts if acc.is_active])
        
        return {
            'customer_id': customer.userId,
            'username': customer.username,
            'full_name': customer.full_name,
            'email': customer.email,
            'customer_since': customer.customer_since.isoformat(),
            'last_login': customer.last_login.isoformat() if customer.last_login else None,
            'is_active': customer.is_active,
            'total_accounts': len(accounts),
            'active_accounts': active_accounts,
            'total_balance': total_balance,
            'accounts': [
                {
                    'account_number': acc.accountNumber,
                    'type': acc.account_type,
                    'balance': acc.getBalance(),
                    'is_active': acc.is_active
                }
                for acc in accounts
            ]
        }
    
    def get_system_statistics(self) -> dict:
        """
        Get system-wide statistics.
        
        Returns:
            Dictionary with system statistics
        """
        all_users = self.user_repository.get_all()
        customers = self.user_repository.get_customers()
        managers = self.user_repository.get_managers()
        active_users = self.user_repository.get_active_users()
        
        all_accounts = self.account_repository.get_all()
        active_accounts = self.account_repository.get_active_accounts()
        total_balance = self.account_repository.get_total_balance()
        
        # Account type breakdown
        account_types = {}
        for account in all_accounts:
            acc_type = account.account_type
            if acc_type not in account_types:
                account_types[acc_type] = {'count': 0, 'balance': 0.0}
            account_types[acc_type]['count'] += 1
            account_types[acc_type]['balance'] += account.getBalance()
        
        return {
            'total_users': len(all_users),
            'total_customers': len(customers),
            'total_managers': len(managers),
            'active_users': len(active_users),
            'total_accounts': len(all_accounts),
            'active_accounts': len(active_accounts),
            'total_system_balance': total_balance,
            'account_types': account_types
        }
    
    def search_customers(self, search_term: str) -> List[Customer]:
        """
        Search for customers by username or full name.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of matching customers
        """
        customers = self.user_repository.get_customers()
        search_term_lower = search_term.lower()
        
        return [
            customer for customer in customers
            if (search_term_lower in customer.username.lower() or
                search_term_lower in (customer.full_name or "").lower())
        ]