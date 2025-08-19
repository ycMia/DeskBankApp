"""
Base UI interface for DeskBank application.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from ..models.user import User, Customer, Manager


class BaseUI(ABC):
    """Abstract base class for user interfaces."""
    
    @abstractmethod
    def display_login_screen(self) -> None:
        """Display the login screen."""
        pass
    
    @abstractmethod
    def display_customer_dashboard(self, customer: Customer) -> None:
        """
        Display the customer dashboard.
        
        Args:
            customer: Customer to display dashboard for
        """
        pass
    
    @abstractmethod
    def display_manager_dashboard(self, manager: Manager) -> None:
        """
        Display the manager dashboard.
        
        Args:
            manager: Manager to display dashboard for
        """
        pass
    
    @abstractmethod
    def prompt(self, message: str, secure: bool = False) -> str:
        """
        Prompt user for input.
        
        Args:
            message: Message to display
            secure: Whether to hide input (for passwords)
            
        Returns:
            User input
        """
        pass
    
    @abstractmethod
    def display_message(self, message: str, message_type: str = "info") -> None:
        """
        Display a message to the user.
        
        Args:
            message: Message to display
            message_type: Type of message (info, warning, error, success)
        """
        pass
    
    @abstractmethod
    def display_table(self, headers: List[str], rows: List[List[str]], 
                     title: Optional[str] = None) -> None:
        """
        Display tabular data.
        
        Args:
            headers: Column headers
            rows: Data rows
            title: Optional table title
        """
        pass
    
    @abstractmethod
    def confirm(self, message: str) -> bool:
        """
        Ask user for confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if user confirmed
        """
        pass
    
    @abstractmethod
    def select_option(self, options: List[str], prompt: str = "Select an option") -> int:
        """
        Let user select from a list of options.
        
        Args:
            options: List of options
            prompt: Prompt message
            
        Returns:
            Index of selected option (0-based)
        """
        pass
    
    @abstractmethod
    def clear_screen(self) -> None:
        """Clear the screen."""
        pass
    
    @abstractmethod
    def display_loading(self, message: str = "Loading...") -> None:
        """
        Display loading indicator.
        
        Args:
            message: Loading message
        """
        pass
    
    @abstractmethod
    def hide_loading(self) -> None:
        """Hide loading indicator."""
        pass
    
    def get_float_input(self, prompt: str, min_value: Optional[float] = None,
                       max_value: Optional[float] = None) -> float:
        """
        Get float input with validation.
        
        Args:
            prompt: Input prompt
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Valid float value
        """
        while True:
            try:
                value_str = self.prompt(prompt)
                value = float(value_str)
                
                if min_value is not None and value < min_value:
                    self.display_message(f"Value must be at least {min_value}", "error")
                    continue
                
                if max_value is not None and value > max_value:
                    self.display_message(f"Value must be at most {max_value}", "error")
                    continue
                
                return value
            except ValueError:
                self.display_message("Please enter a valid number", "error")
    
    def get_int_input(self, prompt: str, min_value: Optional[int] = None,
                     max_value: Optional[int] = None) -> int:
        """
        Get integer input with validation.
        
        Args:
            prompt: Input prompt
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Valid integer value
        """
        while True:
            try:
                value_str = self.prompt(prompt)
                value = int(value_str)
                
                if min_value is not None and value < min_value:
                    self.display_message(f"Value must be at least {min_value}", "error")
                    continue
                
                if max_value is not None and value > max_value:
                    self.display_message(f"Value must be at most {max_value}", "error")
                    continue
                
                return value
            except ValueError:
                self.display_message("Please enter a valid integer", "error")
    
    def format_currency(self, amount: float) -> str:
        """
        Format currency amount.
        
        Args:
            amount: Amount to format
            
        Returns:
            Formatted currency string
        """
        return f"${amount:,.2f}"
    
    def format_date(self, date_obj) -> str:
        """
        Format date for display.
        
        Args:
            date_obj: Date object to format
            
        Returns:
            Formatted date string
        """
        return date_obj.strftime("%Y-%m-%d %H:%M:%S")
    
    def display_account_info(self, account) -> None:
        """
        Display account information.
        
        Args:
            account: Account to display
        """
        headers = ["Property", "Value"]
        rows = [
            ["Account Number", account.accountNumber],
            ["Type", account.getType()],
            ["Balance", self.format_currency(account.getBalance())],
            ["Status", "Active" if account.is_active else "Inactive"]
        ]
        
        self.display_table(headers, rows, f"Account Information")
    
    def display_transaction_history(self, transactions: List, limit: Optional[int] = None) -> None:
        """
        Display transaction history.
        
        Args:
            transactions: List of transactions
            limit: Maximum number to display
        """
        if not transactions:
            self.display_message("No transactions found", "info")
            return
        
        display_transactions = transactions[:limit] if limit else transactions
        
        headers = ["Date", "Type", "Amount", "Description"]
        rows = []
        
        for transaction in display_transactions:
            rows.append([
                self.format_date(transaction.timestamp),
                transaction.type,
                self.format_currency(transaction.amount),
                transaction.description or ""
            ])
        
        title = f"Transaction History ({len(display_transactions)} transactions)"
        if limit and len(transactions) > limit:
            title += f" - Showing latest {limit}"
        
        self.display_table(headers, rows, title)
    
    def display_user_info(self, user: User) -> None:
        """
        Display user information.
        
        Args:
            user: User to display
        """
        headers = ["Property", "Value"]
        rows = [
            ["Username", user.username],
            ["Full Name", user.full_name or "Not set"],
            ["Email", user.email or "Not set"],
            ["Created", self.format_date(user.created_at)],
            ["Last Login", self.format_date(user.last_login) if user.last_login else "Never"],
            ["Status", "Active" if user.is_active else "Inactive"],
            ["User Type", user.__class__.__name__]
        ]
        
        if isinstance(user, Manager):
            rows.extend([
                ["Employee ID", user.employeeId],
                ["Department", user.department],
                ["Hire Date", self.format_date(user.hire_date)]
            ])
        elif isinstance(user, Customer):
            rows.append([
                "Customer Since", self.format_date(user.customer_since)
            ])
        
        self.display_table(headers, rows, "User Information")