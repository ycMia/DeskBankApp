"""
Account repository for managing account data.
"""

from typing import List, Optional
from ..models.account import Account
from .base_repository import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Repository for managing accounts."""
    
    def __init__(self, data_file: Optional[str] = None):
        """
        Initialize the account repository.
        
        Args:
            data_file: Optional file path for data persistence
        """
        super().__init__(data_file)
    
    def _serialize_item(self, account: Account) -> dict:
        """Serialize an account to dictionary."""
        return account.to_dict()
    
    def _deserialize_item(self, data: dict) -> Account:
        """Deserialize dictionary data to account."""
        return Account.from_dict(data)
    
    def _get_item_id(self, account: Account) -> str:
        """Get unique identifier for an account."""
        return account.accountNumber
    
    def find_by_account_number(self, account_number: str) -> Optional[Account]:
        """
        Find an account by account number.
        
        Args:
            account_number: Account number to search for
            
        Returns:
            Account if found, None otherwise
        """
        return self.get_by_id(account_number)
    
    def find_by_owner(self, owner_id: str) -> List[Account]:
        """
        Find all accounts belonging to a specific owner.
        
        Args:
            owner_id: Owner's user ID
            
        Returns:
            List of accounts belonging to the owner
        """
        return [account for account in self._data.values() 
                if account.owner_id == owner_id]
    
    def find_by_type(self, account_type: str) -> List[Account]:
        """
        Find all accounts of a specific type.
        
        Args:
            account_type: Type of account to search for
            
        Returns:
            List of accounts of the specified type
        """
        return [account for account in self._data.values() 
                if account.account_type == account_type]
    
    def get_active_accounts(self) -> List[Account]:
        """
        Get all active accounts.
        
        Returns:
            List of active accounts
        """
        return [account for account in self._data.values() if account.is_active]
    
    def get_inactive_accounts(self) -> List[Account]:
        """
        Get all inactive accounts.
        
        Returns:
            List of inactive accounts
        """
        return [account for account in self._data.values() if not account.is_active]
    
    def get_accounts_with_balance_above(self, minimum_balance: float) -> List[Account]:
        """
        Get accounts with balance above a certain amount.
        
        Args:
            minimum_balance: Minimum balance threshold
            
        Returns:
            List of accounts with balance above the threshold
        """
        return [account for account in self._data.values() 
                if account.getBalance() >= minimum_balance]
    
    def get_accounts_with_balance_below(self, maximum_balance: float) -> List[Account]:
        """
        Get accounts with balance below a certain amount.
        
        Args:
            maximum_balance: Maximum balance threshold
            
        Returns:
            List of accounts with balance below the threshold
        """
        return [account for account in self._data.values() 
                if account.getBalance() <= maximum_balance]
    
    def get_total_balance(self) -> float:
        """
        Get total balance across all accounts.
        
        Returns:
            Total balance of all accounts
        """
        return sum(account.getBalance() for account in self._data.values())
    
    def get_total_balance_by_type(self, account_type: str) -> float:
        """
        Get total balance for accounts of a specific type.
        
        Args:
            account_type: Type of account
            
        Returns:
            Total balance for accounts of the specified type
        """
        return sum(account.getBalance() for account in self._data.values() 
                  if account.account_type == account_type)
    
    def get_total_balance_by_owner(self, owner_id: str) -> float:
        """
        Get total balance for all accounts of a specific owner.
        
        Args:
            owner_id: Owner's user ID
            
        Returns:
            Total balance for the owner's accounts
        """
        return sum(account.getBalance() for account in self._data.values() 
                  if account.owner_id == owner_id)
    
    def update_account_balance(self, account: Account) -> None:
        """
        Update account balance in the repository.
        
        Args:
            account: Account with updated balance
        """
        # This method exists for compatibility with the original interface
        # The balance is automatically updated when the account object is modified
        self.update(account)
    
    def create_account(self, owner_id: str, account_type: str = Account.SAVINGS,
                      initial_balance: float = 0.0) -> Account:
        """
        Create a new account.
        
        Args:
            owner_id: ID of the account owner
            account_type: Type of account
            initial_balance: Initial balance
            
        Returns:
            Created account
        """
        account = Account(initial_balance, account_type, owner_id)
        self.add(account)
        return account
    
    def deactivate_account(self, account_number: str) -> bool:
        """
        Deactivate an account.
        
        Args:
            account_number: Account number to deactivate
            
        Returns:
            True if account was deactivated
        """
        account = self.find_by_account_number(account_number)
        if account:
            account.deactivate()
            self.update(account)
            return True
        return False
    
    def activate_account(self, account_number: str) -> bool:
        """
        Activate an account.
        
        Args:
            account_number: Account number to activate
            
        Returns:
            True if account was activated
        """
        account = self.find_by_account_number(account_number)
        if account:
            account.activate()
            self.update(account)
            return True
        return False
    
    def transfer_ownership(self, account_number: str, new_owner_id: str) -> bool:
        """
        Transfer account ownership to a new owner.
        
        Args:
            account_number: Account to transfer
            new_owner_id: New owner's user ID
            
        Returns:
            True if ownership was transferred
        """
        account = self.find_by_account_number(account_number)
        if account:
            account.owner_id = new_owner_id
            self.update(account)
            return True
        return False