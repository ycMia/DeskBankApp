"""
Transaction model for banking operations.
"""

import uuid
from datetime import datetime
from typing import Optional


class Transaction:
    """Transaction class representing a bank transaction."""
    
    def __init__(self, transaction_type: str, amount: float, account_number: str, 
                 description: Optional[str] = None):
        """
        Initialize a new transaction.
        
        Args:
            transaction_type: Type of transaction (Deposit, Withdrawal, Transfer In/Out)
            amount: Transaction amount
            account_number: Account number associated with the transaction
            description: Optional description of the transaction
        """
        self.transactionId = str(uuid.uuid4())
        self.type = transaction_type
        self.amount = amount
        self.timestamp = datetime.now()
        self.account_number = account_number
        self.description = description or f"{transaction_type} of ${amount:.2f}"
    
    def __str__(self) -> str:
        """String representation of the transaction."""
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {self.type}: ${self.amount:.2f}"
    
    def __repr__(self) -> str:
        """Developer representation of the transaction."""
        return (f"Transaction(id={self.transactionId[:8]}..., type={self.type}, "
                f"amount={self.amount}, account={self.account_number})")
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary for serialization."""
        return {
            'transaction_id': self.transactionId,
            'type': self.type,
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat(),
            'account_number': self.account_number,
            'description': self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Create transaction from dictionary."""
        transaction = cls(
            transaction_type=data['type'],
            amount=data['amount'],
            account_number=data['account_number'],
            description=data.get('description')
        )
        transaction.transactionId = data['transaction_id']
        transaction.timestamp = datetime.fromisoformat(data['timestamp'])
        return transaction