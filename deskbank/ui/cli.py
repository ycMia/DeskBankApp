"""
Command Line Interface implementation for DeskBank.
"""

import os
import getpass
from typing import List, Optional

from .base_ui import BaseUI
from ..models.user import Customer, Manager


class CLI(BaseUI):
    """Command Line Interface implementation."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.loading_active = False
    
    def display_login_screen(self) -> None:
        """Display the login screen."""
        self.clear_screen()
        print("\n" + "="*60)
        print("          🏦 WELCOME TO DESKBANK 🏦")
        print("="*60)
        print("1. Customer Login")
        print("2. Manager Login")
        print("3. Register New Customer")
        print("4. Exit")
        print("="*60)
    
    def display_customer_dashboard(self, customer: Customer) -> None:
        """Display the customer dashboard."""
        print(f"\n{'='*60}")
        print(f"    👤 Customer Dashboard - {customer.full_name}")
        print(f"{'='*60}")
        print("1. View Accounts")
        print("2. Create New Account")
        print("3. Make Deposit")
        print("4. Make Withdrawal")
        print("5. Transfer Funds")
        print("6. View Transaction History")
        print("7. View Profile")
        print("8. Change Password")
        print("9. Logout")
        print("="*60)
    
    def display_manager_dashboard(self, manager: Manager) -> None:
        """Display the manager dashboard."""
        print(f"\n{'='*60}")
        print(f"    👔 Manager Dashboard - {manager.full_name}")
        print(f"{'='*60}")
        print("1. View All Customers")
        print("2. Add New Customer")
        print("3. Remove Customer")
        print("4. View Customer Details")
        print("5. View System Statistics")
        print("6. Account Management")
        print("7. Generate Reports")
        print("8. View Profile")
        print("9. Logout")
        print("="*60)
    
    def prompt(self, message: str, secure: bool = False) -> str:
        """Prompt user for input."""
        if secure:
            return getpass.getpass(message)
        else:
            return input(message)
    
    def display_message(self, message: str, message_type: str = "info") -> None:
        """Display a message to the user."""
        icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        
        icon = icons.get(message_type, "ℹ️")
        print(f"\n{icon} {message}")
    
    def display_table(self, headers: List[str], rows: List[List[str]], 
                     title: Optional[str] = None) -> None:
        """Display tabular data."""
        if title:
            print(f"\n📊 {title}")
            print("-" * len(title))
        
        if not rows:
            print("No data to display.")
            return
        
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print headers
        header_row = " | ".join(
            header.ljust(width) for header, width in zip(headers, col_widths)
        )
        print("\n" + header_row)
        print("-" * len(header_row))
        
        # Print rows
        for row in rows:
            row_str = " | ".join(
                str(cell).ljust(width) for cell, width in zip(row, col_widths)
            )
            print(row_str)
        print()
    
    def confirm(self, message: str) -> bool:
        """Ask user for confirmation."""
        while True:
            response = self.prompt(f"{message} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                self.display_message("Please enter 'y' or 'n'", "warning")
    
    def select_option(self, options: List[str], prompt: str = "Select an option") -> int:
        """Let user select from a list of options."""
        print(f"\n{prompt}:")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = int(self.prompt(f"Enter choice (1-{len(options)}): "))
                if 1 <= choice <= len(options):
                    return choice - 1
                else:
                    self.display_message(f"Please enter a number between 1 and {len(options)}", "error")
            except ValueError:
                self.display_message("Please enter a valid number", "error")
    
    def clear_screen(self) -> None:
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_loading(self, message: str = "Loading...") -> None:
        """Display loading indicator."""
        print(f"⏳ {message}")
        self.loading_active = True
    
    def hide_loading(self) -> None:
        """Hide loading indicator."""
        self.loading_active = False
    
    def display_welcome_banner(self) -> None:
        """Display welcome banner."""
        banner = """
    ██████╗ ███████╗███████╗██╗  ██╗██████╗  █████╗ ███╗   ██╗██╗  ██╗
    ██╔══██╗██╔════╝██╔════╝██║ ██╔╝██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝
    ██║  ██║█████╗  ███████╗█████╔╝ ██████╔╝███████║██╔██╗ ██║█████╔╝ 
    ██║  ██║██╔══╝  ╚════██║██╔═██╗ ██╔══██╗██╔══██║██║╚██╗██║██╔═██╗ 
    ██████╔╝███████╗███████║██║  ██╗██████╔╝██║  ██║██║ ╚████║██║  ██╗
    ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝
                              Your Trusted Banking Partner
        """
        print(banner)
    
    def display_menu_separator(self) -> None:
        """Display menu separator."""
        print("\n" + "─" * 60)
    
    def display_account_summary(self, accounts: List) -> None:
        """Display account summary."""
        if not accounts:
            self.display_message("No accounts found", "info")
            return
        
        headers = ["#", "Account Number", "Type", "Balance", "Status"]
        rows = []
        
        total_balance = 0
        for i, account in enumerate(accounts, 1):
            balance = account.getBalance()
            total_balance += balance
            status = "Active" if account.is_active else "Inactive"
            rows.append([
                str(i),
                account.accountNumber,
                account.getType(),
                self.format_currency(balance),
                status
            ])
        
        self.display_table(headers, rows, "Your Accounts")
        print(f"Total Balance: {self.format_currency(total_balance)}")
    
    def display_quick_stats(self, stats: dict) -> None:
        """Display quick statistics."""
        print("\n📈 Quick Statistics")
        print("-" * 20)
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key}: {self.format_currency(value)}")
            else:
                print(f"{key}: {value}")
    
    def get_account_selection(self, accounts: List, prompt: str = "Select account") -> int:
        """Get account selection from user."""
        if not accounts:
            self.display_message("No accounts available", "error")
            return -1
        
        print(f"\n{prompt}:")
        for i, account in enumerate(accounts, 1):
            status = "Active" if account.is_active else "Inactive"
            print(f"{i}. {account.accountNumber} ({account.getType()}) - "
                  f"{self.format_currency(account.getBalance())} [{status}]")
        
        while True:
            try:
                choice = int(self.prompt(f"Enter choice (1-{len(accounts)}): "))
                if 1 <= choice <= len(accounts):
                    return choice - 1
                else:
                    self.display_message(f"Please enter a number between 1 and {len(accounts)}", "error")
            except ValueError:
                self.display_message("Please enter a valid number", "error")
    
    def display_error_details(self, error: Exception) -> None:
        """Display detailed error information."""
        print(f"\n❌ Error: {str(error)}")
        print("Please try again or contact support if the problem persists.")
    
    def display_operation_result(self, operation: str, success: bool, 
                               details: Optional[str] = None) -> None:
        """Display operation result."""
        if success:
            icon = "✅"
            message = f"{operation} completed successfully"
        else:
            icon = "❌"
            message = f"{operation} failed"
        
        print(f"\n{icon} {message}")
        if details:
            print(f"Details: {details}")
    
    def wait_for_input(self, message: str = "Press Enter to continue...") -> None:
        """Wait for user input before continuing."""
        input(f"\n{message}")
    
    def display_system_info(self) -> None:
        """Display system information."""
        print("\n🖥️  DeskBank System Information")
        print("-" * 30)
        print("Version: 1.0.0")
        print("Built with: Python")
        print("Architecture: Modular MVC")
        print("Security: SHA-256 Password Hashing")
    
    def format_menu_option(self, number: int, text: str, 
                          description: Optional[str] = None) -> str:
        """Format menu option."""
        base = f"{number}. {text}"
        if description:
            base += f" - {description}"
        return base