"""
Customer controller for handling customer interactions.
"""

from typing import List
from ..models.user import Customer
from ..models.account import Account
from ..services.account_service import AccountService
from ..services.transaction_service import TransactionService
from ..services.user_service import UserService
from ..ui.base_ui import BaseUI
from ..config.settings import Settings
from ..utils.validators import Validators


class CustomerController:
    """Controller for customer operations."""
    
    def __init__(self, customer: Customer, ui: BaseUI, 
                 account_service: AccountService,
                 transaction_service: TransactionService,
                 user_service: UserService,
                 settings: Settings):
        """
        Initialize customer controller.
        
        Args:
            customer: Customer instance
            ui: User interface instance
            account_service: Account service
            transaction_service: Transaction service
            user_service: User service
            settings: Application settings
        """
        self.customer = customer
        self.ui = ui
        self.account_service = account_service
        self.transaction_service = transaction_service
        self.user_service = user_service
        self.settings = settings
    
    def run(self) -> None:
        """Run the customer menu loop."""
        while True:
            self.ui.display_customer_dashboard(self.customer)
            choice = self.ui.prompt("Enter your choice: ")
            
            if choice == "1":
                self._view_accounts()
            elif choice == "2":
                self._create_account()
            elif choice == "3":
                self._make_deposit()
            elif choice == "4":
                self._make_withdrawal()
            elif choice == "5":
                self._transfer_funds()
            elif choice == "6":
                self._view_transaction_history()
            elif choice == "7":
                self._view_profile()
            elif choice == "8":
                self._change_password()
            elif choice == "9":
                break
            else:
                self.ui.display_message("Invalid choice. Please try again.", "error")
            
            if choice != "9":
                self.ui.wait_for_input()
    
    def _view_accounts(self) -> None:
        """Display customer accounts."""
        try:
            accounts = self.account_service.get_customer_accounts(self.customer)
            
            if hasattr(self.ui, 'display_account_summary'):
                self.ui.display_account_summary(accounts)
            else:
                if accounts:
                    headers = ["Account Number", "Type", "Balance", "Status"]
                    rows = []
                    total_balance = 0
                    
                    for account in accounts:
                        balance = account.getBalance()
                        total_balance += balance
                        status = "Active" if account.is_active else "Inactive"
                        rows.append([
                            account.accountNumber,
                            account.getType(),
                            self.settings.format_currency(balance),
                            status
                        ])
                    
                    self.ui.display_table(headers, rows, "Your Accounts")
                    self.ui.display_message(
                        f"Total Balance: {self.settings.format_currency(total_balance)}", 
                        "info"
                    )
                else:
                    self.ui.display_message("No accounts found. Create an account first.", "info")
        
        except Exception as e:
            self.ui.display_message(f"Error viewing accounts: {str(e)}", "error")
    
    def _create_account(self) -> None:
        """Create a new account."""
        try:
            # Get account type
            account_types = [Account.SAVINGS, Account.CHECKING, Account.BUSINESS]
            type_index = self.ui.select_option(account_types, "Select account type")
            account_type = account_types[type_index]
            
            # Get initial deposit
            min_balance = self.settings.get_minimum_balance(account_type)
            
            while True:
                amount_str = self.ui.prompt(
                    f"Enter initial deposit (minimum ${min_balance:.2f}): $"
                )
                is_valid, message, amount = Validators.validate_amount(amount_str)
                
                if is_valid and amount >= min_balance:
                    break
                elif is_valid:
                    self.ui.display_message(
                        f"Initial deposit must be at least ${min_balance:.2f}", "error"
                    )
                else:
                    self.ui.display_message(message, "error")
            
            # Create account
            account = self.account_service.create_account(
                customer=self.customer,
                account_type=account_type,
                initial_deposit=amount
            )
            
            self.ui.display_message(
                f"Account #{account.accountNumber} created successfully!", "success"
            )
            
            if hasattr(self.ui, 'display_account_info'):
                self.ui.display_account_info(account)
        
        except Exception as e:
            self.ui.display_message(f"Error creating account: {str(e)}", "error")
    
    def _make_deposit(self) -> None:
        """Make a deposit to an account."""
        try:
            accounts = self.account_service.get_customer_accounts(self.customer)
            active_accounts = [acc for acc in accounts if acc.is_active]
            
            if not active_accounts:
                self.ui.display_message("No active accounts available.", "error")
                return
            
            # Select account
            if hasattr(self.ui, 'get_account_selection'):
                account_index = self.ui.get_account_selection(active_accounts, "Select account for deposit")
            else:
                account_options = [
                    f"{acc.accountNumber} ({acc.getType()}) - {self.settings.format_currency(acc.getBalance())}"
                    for acc in active_accounts
                ]
                account_index = self.ui.select_option(account_options, "Select account for deposit")
            
            if account_index < 0:
                return
            
            selected_account = active_accounts[account_index]
            
            # Get deposit amount
            while True:
                amount_str = self.ui.prompt("Enter deposit amount: $")
                is_valid, message, amount = Validators.validate_amount(amount_str)
                
                if is_valid:
                    break
                else:
                    self.ui.display_message(message, "error")
            
            # Get optional description
            description = self.ui.prompt("Enter description (optional): ")
            if description:
                is_valid, message = Validators.validate_transaction_description(description)
                if not is_valid:
                    self.ui.display_message(f"Description error: {message}", "warning")
                    description = None
            
            # Make deposit
            transaction = self.transaction_service.make_deposit(
                account_number=selected_account.accountNumber,
                amount=amount,
                description=description or None
            )
            
            self.ui.display_message(
                f"Deposit of {self.settings.format_currency(amount)} completed successfully!", 
                "success"
            )
            self.ui.display_message(
                f"New balance: {self.settings.format_currency(selected_account.getBalance())}", 
                "info"
            )
            self.ui.display_message(f"Transaction ID: {transaction.transactionId}", "info")
        
        except Exception as e:
            self.ui.display_message(f"Error making deposit: {str(e)}", "error")
    
    def _make_withdrawal(self) -> None:
        """Make a withdrawal from an account."""
        try:
            accounts = self.account_service.get_customer_accounts(self.customer)
            active_accounts = [acc for acc in accounts if acc.is_active and acc.getBalance() > 0]
            
            if not active_accounts:
                self.ui.display_message("No active accounts with funds available.", "error")
                return
            
            # Select account
            if hasattr(self.ui, 'get_account_selection'):
                account_index = self.ui.get_account_selection(active_accounts, "Select account for withdrawal")
            else:
                account_options = [
                    f"{acc.accountNumber} ({acc.getType()}) - {self.settings.format_currency(acc.getBalance())}"
                    for acc in active_accounts
                ]
                account_index = self.ui.select_option(account_options, "Select account for withdrawal")
            
            if account_index < 0:
                return
            
            selected_account = active_accounts[account_index]
            max_amount = selected_account.getBalance()
            
            # Check minimum balance requirement
            min_balance = self.settings.get_minimum_balance(selected_account.getType())
            available_amount = max_amount - min_balance
            
            if available_amount <= 0:
                self.ui.display_message(
                    f"Cannot withdraw. Minimum balance of {self.settings.format_currency(min_balance)} required.", 
                    "error"
                )
                return
            
            # Get withdrawal amount
            while True:
                amount_str = self.ui.prompt(
                    f"Enter withdrawal amount (max ${available_amount:.2f}): $"
                )
                is_valid, message, amount = Validators.validate_amount(amount_str)
                
                if is_valid and amount <= available_amount:
                    break
                elif is_valid:
                    self.ui.display_message(
                        f"Amount exceeds available funds (${available_amount:.2f})", "error"
                    )
                else:
                    self.ui.display_message(message, "error")
            
            # Check daily limit
            if not self.transaction_service.check_daily_limit(selected_account.accountNumber, amount):
                daily_limit = self.transaction_service.get_daily_transaction_limit(selected_account.getType())
                self.ui.display_message(
                    f"Transaction would exceed daily limit of {self.settings.format_currency(daily_limit)}", 
                    "error"
                )
                return
            
            # Get optional description
            description = self.ui.prompt("Enter description (optional): ")
            if description:
                is_valid, message = Validators.validate_transaction_description(description)
                if not is_valid:
                    self.ui.display_message(f"Description error: {message}", "warning")
                    description = None
            
            # Confirm withdrawal
            if not self.ui.confirm(f"Confirm withdrawal of {self.settings.format_currency(amount)}?"):
                self.ui.display_message("Withdrawal cancelled.", "info")
                return
            
            # Make withdrawal
            transaction = self.transaction_service.make_withdrawal(
                account_number=selected_account.accountNumber,
                amount=amount,
                description=description or None
            )
            
            self.ui.display_message(
                f"Withdrawal of {self.settings.format_currency(amount)} completed successfully!", 
                "success"
            )
            self.ui.display_message(
                f"New balance: {self.settings.format_currency(selected_account.getBalance())}", 
                "info"
            )
            self.ui.display_message(f"Transaction ID: {transaction.transactionId}", "info")
        
        except Exception as e:
            self.ui.display_message(f"Error making withdrawal: {str(e)}", "error")
    
    def _transfer_funds(self) -> None:
        """Transfer funds between accounts."""
        try:
            accounts = self.account_service.get_customer_accounts(self.customer)
            active_accounts = [acc for acc in accounts if acc.is_active]
            
            if len(active_accounts) < 2:
                self.ui.display_message("You need at least 2 active accounts to transfer funds.", "error")
                return
            
            # Select source account
            source_accounts = [acc for acc in active_accounts if acc.getBalance() > 0]
            if not source_accounts:
                self.ui.display_message("No accounts with funds available for transfer.", "error")
                return
            
            if hasattr(self.ui, 'get_account_selection'):
                from_index = self.ui.get_account_selection(source_accounts, "Select source account")
            else:
                from_options = [
                    f"{acc.accountNumber} ({acc.getType()}) - {self.settings.format_currency(acc.getBalance())}"
                    for acc in source_accounts
                ]
                from_index = self.ui.select_option(from_options, "Select source account")
            
            if from_index < 0:
                return
            
            from_account = source_accounts[from_index]
            
            # Select destination account
            to_accounts = [acc for acc in active_accounts if acc.accountNumber != from_account.accountNumber]
            
            if hasattr(self.ui, 'get_account_selection'):
                to_index = self.ui.get_account_selection(to_accounts, "Select destination account")
            else:
                to_options = [
                    f"{acc.accountNumber} ({acc.getType()}) - {self.settings.format_currency(acc.getBalance())}"
                    for acc in to_accounts
                ]
                to_index = self.ui.select_option(to_options, "Select destination account")
            
            if to_index < 0:
                return
            
            to_account = to_accounts[to_index]
            
            # Get transfer amount
            min_balance = self.settings.get_minimum_balance(from_account.getType())
            max_amount = from_account.getBalance() - min_balance
            
            if max_amount <= 0:
                self.ui.display_message(
                    f"Cannot transfer. Minimum balance of {self.settings.format_currency(min_balance)} required.", 
                    "error"
                )
                return
            
            while True:
                amount_str = self.ui.prompt(
                    f"Enter transfer amount (max ${max_amount:.2f}): $"
                )
                is_valid, message, amount = Validators.validate_amount(amount_str)
                
                if is_valid and amount <= max_amount:
                    break
                elif is_valid:
                    self.ui.display_message(
                        f"Amount exceeds available funds (${max_amount:.2f})", "error"
                    )
                else:
                    self.ui.display_message(message, "error")
            
            # Get optional description
            description = self.ui.prompt("Enter description (optional): ")
            if description:
                is_valid, message = Validators.validate_transaction_description(description)
                if not is_valid:
                    self.ui.display_message(f"Description error: {message}", "warning")
                    description = None
            
            # Confirm transfer
            if not self.ui.confirm(
                f"Transfer {self.settings.format_currency(amount)} from "
                f"{from_account.accountNumber} to {to_account.accountNumber}?"
            ):
                self.ui.display_message("Transfer cancelled.", "info")
                return
            
            # Make transfer
            transaction = self.transaction_service.transfer_funds(
                from_account_number=from_account.accountNumber,
                to_account_number=to_account.accountNumber,
                amount=amount,
                description=description or None
            )
            
            self.ui.display_message(
                f"Transfer of {self.settings.format_currency(amount)} completed successfully!", 
                "success"
            )
            self.ui.display_message(f"Transaction ID: {transaction.transactionId}", "info")
        
        except Exception as e:
            self.ui.display_message(f"Error transferring funds: {str(e)}", "error")
    
    def _view_transaction_history(self) -> None:
        """View transaction history for an account."""
        try:
            accounts = self.account_service.get_customer_accounts(self.customer)
            
            if not accounts:
                self.ui.display_message("No accounts found.", "error")
                return
            
            # Select account
            if hasattr(self.ui, 'get_account_selection'):
                account_index = self.ui.get_account_selection(accounts, "Select account to view history")
            else:
                account_options = [
                    f"{acc.accountNumber} ({acc.getType()}) - {self.settings.format_currency(acc.getBalance())}"
                    for acc in accounts
                ]
                account_index = self.ui.select_option(account_options, "Select account to view history")
            
            if account_index < 0:
                return
            
            selected_account = accounts[account_index]
            
            # Get transaction history
            limit = self.settings.get("table_max_rows", 50)
            transactions = self.transaction_service.get_transaction_history(
                selected_account.accountNumber, limit
            )
            
            if hasattr(self.ui, 'display_transaction_history'):
                self.ui.display_transaction_history(transactions, limit)
            else:
                if transactions:
                    headers = ["Date", "Type", "Amount", "Description"]
                    rows = []
                    
                    for transaction in transactions:
                        rows.append([
                            transaction.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                            transaction.type,
                            self.settings.format_currency(transaction.amount),
                            transaction.description or ""
                        ])
                    
                    title = f"Transaction History - Account #{selected_account.accountNumber}"
                    self.ui.display_table(headers, rows, title)
                else:
                    self.ui.display_message("No transactions found.", "info")
        
        except Exception as e:
            self.ui.display_message(f"Error viewing transaction history: {str(e)}", "error")
    
    def _view_profile(self) -> None:
        """View customer profile information."""
        try:
            if hasattr(self.ui, 'display_user_info'):
                self.ui.display_user_info(self.customer)
            else:
                headers = ["Property", "Value"]
                rows = [
                    ["Username", self.customer.username],
                    ["Full Name", self.customer.full_name or "Not set"],
                    ["Email", self.customer.email or "Not set"],
                    ["Customer Since", self.customer.customer_since.strftime("%Y-%m-%d")],
                    ["Last Login", self.customer.last_login.strftime("%Y-%m-%d %H:%M:%S") if self.customer.last_login else "Never"],
                    ["Account Status", "Active" if self.customer.is_active else "Inactive"]
                ]
                
                self.ui.display_table(headers, rows, "Customer Profile")
            
            # Show account summary
            summary = self.account_service.get_account_summary(self.customer)
            self.ui.display_message(
                f"Total Accounts: {summary['total_accounts']} | "
                f"Total Balance: {self.settings.format_currency(summary['total_balance'])}", 
                "info"
            )
        
        except Exception as e:
            self.ui.display_message(f"Error viewing profile: {str(e)}", "error")
    
    def _change_password(self) -> None:
        """Change customer password."""
        try:
            current_password = self.ui.prompt("Enter current password: ", secure=True)
            
            if not self.customer.verify_password(current_password):
                self.ui.display_message("Current password is incorrect.", "error")
                return
            
            # Get new password
            while True:
                new_password = self.ui.prompt("Enter new password: ", secure=True)
                is_valid, message = self.settings.validate_password_policy(new_password)
                
                if is_valid:
                    confirm_password = self.ui.prompt("Confirm new password: ", secure=True)
                    if new_password == confirm_password:
                        break
                    else:
                        self.ui.display_message("Passwords do not match.", "error")
                else:
                    self.ui.display_message(message, "error")
            
            # Change password
            success = self.user_service.change_user_password(
                user_id=self.customer.userId,
                old_password=current_password,
                new_password=new_password
            )
            
            if success:
                self.ui.display_message("Password changed successfully!", "success")
            else:
                self.ui.display_message("Failed to change password.", "error")
        
        except Exception as e:
            self.ui.display_message(f"Error changing password: {str(e)}", "error")