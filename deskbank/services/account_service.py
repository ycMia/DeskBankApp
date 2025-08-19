"""
Account service for managing bank accounts.
"""

from typing import List, Optional
from ..models.account import Account
from ..models.user import Customer
from ..repositories.account_repository import AccountRepository


class AccountService:
    """Service for managing bank accounts."""
    
    def __init__(self, account_repository: AccountRepository):
        """
        Initialize the account service.
        
        Args:
            account_repository: Repository for account data
        """
        self.account_repository = account_repository
    
    def create_account(self, customer: Customer, account_type: str = Account.SAVINGS,
                      initial_deposit: float = 0.0) -> Account:
        """
        Create a new account for a customer.
        
        Args:
            customer: Customer who owns the account
            account_type: Type of account to create
            initial_deposit: Initial deposit amount
            
        Returns:
            Created account
            
        Raises:
            ValueError: If initial deposit is negative
        """
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative")
        
        # Validate account type
        valid_types = [Account.SAVINGS, Account.CHECKING, Account.BUSINESS]
        if account_type not in valid_types:
            raise ValueError(f"Invalid account type. Must be one of: {valid_types}")
        
        account = self.account_repository.create_account(
            owner_id=customer.userId,
            account_type=account_type,
            initial_balance=initial_deposit
        )
        
        # Add account to customer's account list
        customer.add_account(account)
        
        return account
    
    def get_customer_accounts(self, customer: Customer) -> List[Account]:
        """
        Get all accounts belonging to a customer.
        
        Args:
            customer: Customer to get accounts for
            
        Returns:
            List of customer's accounts
        """
        return self.account_repository.find_by_owner(customer.userId)
    
    def get_account(self, account_number: str) -> Optional[Account]:
        """
        Get an account by account number.
        
        Args:
            account_number: Account number to find
            
        Returns:
            Account if found, None otherwise
        """
        return self.account_repository.find_by_account_number(account_number)
    
    def get_account_balance(self, account_number: str) -> float:
        """
        Get the balance of an account.
        
        Args:
            account_number: Account number
            
        Returns:
            Account balance
            
        Raises:
            ValueError: If account not found
        """
        account = self.get_account(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        return account.getBalance()
    
    def get_accounts_by_type(self, account_type: str) -> List[Account]:
        """
        Get all accounts of a specific type.
        
        Args:
            account_type: Type of account
            
        Returns:
            List of accounts of the specified type
        """
        return self.account_repository.find_by_type(account_type)
    
    def get_active_accounts(self) -> List[Account]:
        """
        Get all active accounts.
        
        Returns:
            List of active accounts
        """
        return self.account_repository.get_active_accounts()
    
    def get_inactive_accounts(self) -> List[Account]:
        """
        Get all inactive accounts.
        
        Returns:
            List of inactive accounts
        """
        return self.account_repository.get_inactive_accounts()
    
    def deactivate_account(self, account_number: str) -> bool:
        """
        Deactivate an account.
        
        Args:
            account_number: Account number to deactivate
            
        Returns:
            True if account was deactivated
        """
        return self.account_repository.deactivate_account(account_number)
    
    def activate_account(self, account_number: str) -> bool:
        """
        Activate an account.
        
        Args:
            account_number: Account number to activate
            
        Returns:
            True if account was activated
        """
        return self.account_repository.activate_account(account_number)
    
    def close_account(self, account_number: str) -> bool:
        """
        Close an account (deactivate and ensure zero balance).
        
        Args:
            account_number: Account number to close
            
        Returns:
            True if account was closed
            
        Raises:
            ValueError: If account has non-zero balance or not found
        """
        account = self.get_account(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        if account.getBalance() != 0:
            raise ValueError(f"Cannot close account with non-zero balance: ${account.getBalance()}")
        
        return self.deactivate_account(account_number)
    
    def transfer_account_ownership(self, account_number: str, new_owner: Customer) -> bool:
        """
        Transfer account ownership to a new customer.
        
        Args:
            account_number: Account to transfer
            new_owner: New owner of the account
            
        Returns:
            True if ownership was transferred
            
        Raises:
            ValueError: If account not found
        """
        account = self.get_account(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        # Update ownership in repository
        success = self.account_repository.transfer_ownership(account_number, new_owner.userId)
        
        if success:
            # Add to new owner's account list
            new_owner.add_account(account)
        
        return success
    
    def get_account_summary(self, customer: Customer) -> dict:
        """
        Get a summary of all accounts for a customer.
        
        Args:
            customer: Customer to get summary for
            
        Returns:
            Dictionary with account summary information
        """
        accounts = self.get_customer_accounts(customer)
        
        total_balance = sum(account.getBalance() for account in accounts)
        active_accounts = len([acc for acc in accounts if acc.is_active])
        inactive_accounts = len([acc for acc in accounts if not acc.is_active])
        
        account_types = {}
        for account in accounts:
            account_type = account.account_type
            if account_type not in account_types:
                account_types[account_type] = {'count': 0, 'balance': 0.0}
            account_types[account_type]['count'] += 1
            account_types[account_type]['balance'] += account.getBalance()
        
        return {
            'total_accounts': len(accounts),
            'active_accounts': active_accounts,
            'inactive_accounts': inactive_accounts,
            'total_balance': total_balance,
            'account_types': account_types,
            'accounts': [
                {
                    'account_number': acc.accountNumber,
                    'type': acc.account_type,
                    'balance': acc.getBalance(),
                    'is_active': acc.is_active,
                    'transaction_count': len(acc.transactions)
                }
                for acc in accounts
            ]
        }
    
    def validate_account_access(self, customer: Customer, account_number: str) -> bool:
        """
        Validate if a customer has access to a specific account.
        
        Args:
            customer: Customer requesting access
            account_number: Account number to validate
            
        Returns:
            True if customer has access to the account
        """
        account = self.get_account(account_number)
        if not account:
            return False
        
        return account.owner_id == customer.userId
    
    def get_minimum_balance_requirement(self, account_type: str) -> float:
        """
        Get minimum balance requirement for an account type.
        
        Args:
            account_type: Type of account
            
        Returns:
            Minimum balance requirement
        """
        requirements = {
            Account.SAVINGS: 100.0,
            Account.CHECKING: 50.0,
            Account.BUSINESS: 500.0
        }
        return requirements.get(account_type, 0.0)
    
    def check_minimum_balance(self, account_number: str) -> bool:
        """
        Check if an account meets minimum balance requirements.
        
        Args:
            account_number: Account number to check
            
        Returns:
            True if account meets minimum balance
            
        Raises:
            ValueError: If account not found
        """
        account = self.get_account(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        minimum_required = self.get_minimum_balance_requirement(account.account_type)
        return account.getBalance() >= minimum_required