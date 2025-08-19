"""
Account model for banking operations.
"""

import uuid
from typing import List, Optional
from decimal import Decimal, ROUND_HALF_UP

from .transaction import Transaction


class Account:
    """Account class representing a bank account."""
    
    # Account types
    SAVINGS = "Savings"
    CHECKING = "Checking"
    BUSINESS = "Business"
    
    def __init__(self, balance: float = 0.0, account_type: str = SAVINGS, 
                 owner_id: Optional[str] = None):
        """
        Initialize a new account.
        
        Args:
            balance: Initial account balance
            account_type: Type of account (Savings, Checking, Business)
            owner_id: ID of the account owner
        """
        self.accountNumber = self._generate_account_number()
        self.balance = Decimal(str(balance)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.account_type = account_type
        self.owner_id = owner_id
        self.transactions: List[Transaction] = []
        self.is_active = True
    
    def _generate_account_number(self) -> str:
        """Generate a unique account number."""
        return str(uuid.uuid4())[:8].upper()
    
    def getBalance(self) -> float:
        """Get the current balance of the account."""
        return float(self.balance)
    
    def getType(self) -> str:
        """Get the type of the account."""
        return self.account_type
    
    def deposit(self, amount: float, description: Optional[str] = None) -> Transaction:
        """
        Deposit money into the account.
        
        Args:
            amount: Amount to deposit
            description: Optional description
            
        Returns:
            Transaction object
            
        Raises:
            ValueError: If amount is not positive or account is inactive
        """
        if not self.is_active:
            raise ValueError("Cannot deposit to inactive account")
        
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        amount_decimal = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self.balance += amount_decimal
        
        transaction = Transaction(
            transaction_type="Deposit",
            amount=float(amount_decimal),
            account_number=self.accountNumber,
            description=description
        )
        self.transactions.append(transaction)
        return transaction
    
    def withdraw(self, amount: float, description: Optional[str] = None) -> Transaction:
        """
        Withdraw money from the account.
        
        Args:
            amount: Amount to withdraw
            description: Optional description
            
        Returns:
            Transaction object
            
        Raises:
            ValueError: If amount is invalid, insufficient funds, or account is inactive
        """
        if not self.is_active:
            raise ValueError("Cannot withdraw from inactive account")
        
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        amount_decimal = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if self.balance < amount_decimal:
            raise ValueError(f"Insufficient funds. Available: ${self.balance}")
        
        self.balance -= amount_decimal
        
        transaction = Transaction(
            transaction_type="Withdrawal",
            amount=float(amount_decimal),
            account_number=self.accountNumber,
            description=description
        )
        self.transactions.append(transaction)
        return transaction
    
    def transfer_to(self, to_account: 'Account', amount: float, 
                   description: Optional[str] = None) -> Transaction:
        """
        Transfer money from this account to another account.
        
        Args:
            to_account: Destination account
            amount: Amount to transfer
            description: Optional description
            
        Returns:
            Transaction object for the outgoing transfer
            
        Raises:
            ValueError: If transfer is invalid
        """
        if not self.is_active or not to_account.is_active:
            raise ValueError("Cannot transfer between inactive accounts")
        
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        
        amount_decimal = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        if self.balance < amount_decimal:
            raise ValueError(f"Insufficient funds. Available: ${self.balance}")
        
        # Debit from source account
        self.balance -= amount_decimal
        out_transaction = Transaction(
            transaction_type="Transfer Out",
            amount=float(amount_decimal),
            account_number=self.accountNumber,
            description=description or f"Transfer to {to_account.accountNumber}"
        )
        self.transactions.append(out_transaction)
        
        # Credit to destination account
        to_account.balance += amount_decimal
        in_transaction = Transaction(
            transaction_type="Transfer In",
            amount=float(amount_decimal),
            account_number=to_account.accountNumber,
            description=description or f"Transfer from {self.accountNumber}"
        )
        to_account.transactions.append(in_transaction)
        
        return out_transaction
    
    def get_transaction_history(self, limit: Optional[int] = None) -> List[Transaction]:
        """
        Get transaction history for the account.
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions, newest first
        """
        sorted_transactions = sorted(self.transactions, 
                                   key=lambda t: t.timestamp, reverse=True)
        return sorted_transactions[:limit] if limit else sorted_transactions
    
    def deactivate(self) -> None:
        """Deactivate the account."""
        self.is_active = False
    
    def activate(self) -> None:
        """Activate the account."""
        self.is_active = True
    
    def __str__(self) -> str:
        """String representation of the account."""
        status = "Active" if self.is_active else "Inactive"
        return f"Account #{self.accountNumber} ({self.account_type}) - ${self.balance} [{status}]"
    
    def __repr__(self) -> str:
        """Developer representation of the account."""
        return (f"Account(number={self.accountNumber}, type={self.account_type}, "
                f"balance={self.balance}, active={self.is_active})")
    
    def to_dict(self) -> dict:
        """Convert account to dictionary for serialization."""
        return {
            'account_number': self.accountNumber,
            'balance': float(self.balance),
            'account_type': self.account_type,
            'owner_id': self.owner_id,
            'is_active': self.is_active,
            'transactions': [t.to_dict() for t in self.transactions]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Account':
        """Create account from dictionary."""
        account = cls(
            balance=data['balance'],
            account_type=data['account_type'],
            owner_id=data.get('owner_id')
        )
        account.accountNumber = data['account_number']
        account.is_active = data.get('is_active', True)
        
        # Restore transactions
        account.transactions = [
            Transaction.from_dict(t_data) for t_data in data.get('transactions', [])
        ]
        
        return account