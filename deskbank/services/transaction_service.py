"""
Transaction service for handling banking transactions.
"""

from typing import Optional, List
from decimal import Decimal

from ..models.transaction import Transaction
from ..models.account import Account
from ..repositories.account_repository import AccountRepository


class TransactionService:
    """Service for handling banking transactions."""
    
    def __init__(self, account_repository: AccountRepository):
        """
        Initialize the transaction service.
        
        Args:
            account_repository: Repository for account data
        """
        self.account_repository = account_repository
    
    def make_deposit(self, account_number: str, amount: float, 
                    description: Optional[str] = None) -> Transaction:
        """
        Make a deposit to an account.
        
        Args:
            account_number: Account number to deposit to
            amount: Amount to deposit
            description: Optional transaction description
            
        Returns:
            Transaction object
            
        Raises:
            ValueError: If account not found or deposit fails
        """
        account = self.account_repository.find_by_account_number(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        if not account.is_active:
            raise ValueError(f"Account {account_number} is inactive")
        
        transaction = account.deposit(amount, description)
        self.account_repository.update(account)
        return transaction
    
    def make_withdrawal(self, account_number: str, amount: float,
                       description: Optional[str] = None) -> Transaction:
        """
        Make a withdrawal from an account.
        
        Args:
            account_number: Account number to withdraw from
            amount: Amount to withdraw
            description: Optional transaction description
            
        Returns:
            Transaction object
            
        Raises:
            ValueError: If account not found or withdrawal fails
        """
        account = self.account_repository.find_by_account_number(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        if not account.is_active:
            raise ValueError(f"Account {account_number} is inactive")
        
        transaction = account.withdraw(amount, description)
        self.account_repository.update(account)
        return transaction
    
    def transfer_funds(self, from_account_number: str, to_account_number: str,
                      amount: float, description: Optional[str] = None) -> Transaction:
        """
        Transfer funds between accounts.
        
        Args:
            from_account_number: Source account number
            to_account_number: Destination account number
            amount: Amount to transfer
            description: Optional transaction description
            
        Returns:
            Transaction object for the outgoing transfer
            
        Raises:
            ValueError: If accounts not found or transfer fails
        """
        if from_account_number == to_account_number:
            raise ValueError("Cannot transfer to the same account")
        
        from_account = self.account_repository.find_by_account_number(from_account_number)
        to_account = self.account_repository.find_by_account_number(to_account_number)
        
        if not from_account:
            raise ValueError(f"Source account {from_account_number} not found")
        
        if not to_account:
            raise ValueError(f"Destination account {to_account_number} not found")
        
        if not from_account.is_active:
            raise ValueError(f"Source account {from_account_number} is inactive")
        
        if not to_account.is_active:
            raise ValueError(f"Destination account {to_account_number} is inactive")
        
        transaction = from_account.transfer_to(to_account, amount, description)
        
        # Update both accounts in the repository
        self.account_repository.update(from_account)
        self.account_repository.update(to_account)
        
        return transaction
    
    def get_account_balance(self, account_number: str) -> float:
        """
        Get the current balance of an account.
        
        Args:
            account_number: Account number
            
        Returns:
            Account balance
            
        Raises:
            ValueError: If account not found
        """
        account = self.account_repository.find_by_account_number(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        return account.getBalance()
    
    def get_transaction_history(self, account_number: str,
                              limit: Optional[int] = None) -> List[Transaction]:
        """
        Get transaction history for an account.
        
        Args:
            account_number: Account number
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions, newest first
            
        Raises:
            ValueError: If account not found
        """
        account = self.account_repository.find_by_account_number(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        return account.get_transaction_history(limit)
    
    def validate_transfer_amount(self, amount: float) -> bool:
        """
        Validate if a transfer amount is acceptable.
        
        Args:
            amount: Amount to validate
            
        Returns:
            True if amount is valid
        """
        try:
            amount_decimal = Decimal(str(amount))
            return amount_decimal > 0 and amount_decimal.as_tuple().exponent >= -2
        except (ValueError, TypeError):
            return False
    
    def calculate_transfer_fee(self, amount: float, 
                             from_account_type: str, 
                             to_account_type: str) -> float:
        """
        Calculate transfer fee (placeholder for future implementation).
        
        Args:
            amount: Transfer amount
            from_account_type: Source account type
            to_account_type: Destination account type
            
        Returns:
            Transfer fee (currently always 0)
        """
        # Placeholder for fee calculation logic
        # Could implement different fees based on account types, amount tiers, etc.
        return 0.0
    
    def get_daily_transaction_limit(self, account_type: str) -> float:
        """
        Get daily transaction limit for an account type.
        
        Args:
            account_type: Type of account
            
        Returns:
            Daily transaction limit
        """
        limits = {
            Account.SAVINGS: 5000.0,
            Account.CHECKING: 10000.0,
            Account.BUSINESS: 50000.0
        }
        return limits.get(account_type, 1000.0)
    
    def check_daily_limit(self, account_number: str, amount: float) -> bool:
        """
        Check if a transaction would exceed daily limits.
        
        Args:
            account_number: Account number
            amount: Transaction amount
            
        Returns:
            True if transaction is within limits
            
        Raises:
            ValueError: If account not found
        """
        account = self.account_repository.find_by_account_number(account_number)
        if not account:
            raise ValueError(f"Account {account_number} not found")
        
        daily_limit = self.get_daily_transaction_limit(account.account_type)
        
        # Calculate today's transaction total
        from datetime import datetime, date
        today = date.today()
        
        today_transactions = [
            t for t in account.transactions
            if t.timestamp.date() == today and t.type in ['Withdrawal', 'Transfer Out']
        ]
        
        today_total = sum(t.amount for t in today_transactions)
        
        return (today_total + amount) <= daily_limit
    
    def reverse_transaction(self, transaction_id: str) -> bool:
        """
        Reverse a transaction (placeholder for future implementation).
        
        Args:
            transaction_id: ID of transaction to reverse
            
        Returns:
            True if transaction was reversed
        """
        # Placeholder for transaction reversal logic
        # Would need to implement proper reversal mechanism
        # with appropriate checks and balances
        return False