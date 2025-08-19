"""
Manager controller for handling manager interactions.
"""

from typing import List
from ..models.user import Manager, Customer
from ..services.user_service import UserService
from ..services.account_service import AccountService
from ..services.transaction_service import TransactionService
from ..services.authentication_service import AuthenticationService
from ..ui.base_ui import BaseUI
from ..config.settings import Settings
from ..utils.validators import Validators


class ManagerController:
    """Controller for manager operations."""
    
    def __init__(self, manager: Manager, ui: BaseUI,
                 user_service: UserService,
                 account_service: AccountService,
                 transaction_service: TransactionService,
                 auth_service: AuthenticationService,
                 settings: Settings):
        """
        Initialize manager controller.
        
        Args:
            manager: Manager instance
            ui: User interface instance
            user_service: User service
            account_service: Account service
            transaction_service: Transaction service
            auth_service: Authentication service
            settings: Application settings
        """
        self.manager = manager
        self.ui = ui
        self.user_service = user_service
        self.account_service = account_service
        self.transaction_service = transaction_service
        self.auth_service = auth_service
        self.settings = settings
    
    def run(self) -> None:
        """Run the manager menu loop."""
        while True:
            self.ui.display_manager_dashboard(self.manager)
            choice = self.ui.prompt("Enter your choice: ")
            
            if choice == "1":
                self._view_all_customers()
            elif choice == "2":
                self._add_new_customer()
            elif choice == "3":
                self._remove_customer()
            elif choice == "4":
                self._view_customer_details()
            elif choice == "5":
                self._view_system_statistics()
            elif choice == "6":
                self._account_management()
            elif choice == "7":
                self._generate_reports()
            elif choice == "8":
                self._view_profile()
            elif choice == "9":
                break
            else:
                self.ui.display_message("Invalid choice. Please try again.", "error")
            
            if choice != "9":
                self.ui.wait_for_input()
    
    def _view_all_customers(self) -> None:
        """View all customers in the system."""
        try:
            customers = self.user_service.get_all_customers()
            
            if customers:
                headers = ["Username", "Full Name", "Email", "Accounts", "Total Balance", "Status"]
                rows = []
                
                for customer in customers:
                    # Get customer account summary
                    accounts = self.account_service.get_customer_accounts(customer)
                    total_balance = sum(acc.getBalance() for acc in accounts)
                    
                    rows.append([
                        customer.username,
                        customer.full_name or "Not set",
                        customer.email or "Not set",
                        str(len(accounts)),
                        self.settings.format_currency(total_balance),
                        "Active" if customer.is_active else "Inactive"
                    ])
                
                self.ui.display_table(headers, rows, f"All Customers ({len(customers)} total)")
            else:
                self.ui.display_message("No customers found.", "info")
        
        except Exception as e:
            self.ui.display_message(f"Error viewing customers: {str(e)}", "error")
    
    def _add_new_customer(self) -> None:
        """Add a new customer (manager function)."""
        try:
            self.ui.display_message("Add New Customer", "info")
            
            # Get and validate username
            while True:
                username = self.ui.prompt("Enter username: ")
                is_valid, message = Validators.validate_username(username)
                if is_valid and not self.user_service.get_user_by_username(username):
                    break
                elif not is_valid:
                    self.ui.display_message(message, "error")
                else:
                    self.ui.display_message("Username already exists. Please choose another.", "error")
            
            # Get and validate password
            while True:
                password = self.ui.prompt("Enter password: ", secure=True)
                is_valid, message = self.settings.validate_password_policy(password)
                if is_valid:
                    confirm_password = self.ui.prompt("Confirm password: ", secure=True)
                    if password == confirm_password:
                        break
                    else:
                        self.ui.display_message("Passwords do not match.", "error")
                else:
                    self.ui.display_message(message, "error")
            
            # Get optional information
            email = self.ui.prompt("Enter email (optional): ")
            if email:
                is_valid, message = Validators.validate_email(email)
                if not is_valid:
                    self.ui.display_message(f"Email error: {message}", "warning")
                    email = ""
            
            full_name = self.ui.prompt("Enter full name (optional): ")
            if full_name:
                is_valid, message = Validators.validate_full_name(full_name)
                if not is_valid:
                    self.ui.display_message(f"Name error: {message}", "warning")
                    full_name = ""
            
            # Create customer
            customer = self.user_service.register_customer(
                username=username,
                password=password,
                email=email or None,
                full_name=full_name or None
            )
            
            self.ui.display_message(f"Customer {username} created successfully!", "success")
            
            # Ask if they want to create an initial account
            if self.ui.confirm("Create an initial account for this customer?"):
                self._create_customer_account(customer)
        
        except Exception as e:
            self.ui.display_message(f"Error creating customer: {str(e)}", "error")
    
    def _remove_customer(self) -> None:
        """Remove a customer from the system."""
        try:
            customers = self.user_service.get_all_customers()
            
            if not customers:
                self.ui.display_message("No customers found.", "error")
                return
            
            # Select customer to remove
            customer_options = [
                f"{c.username} ({c.full_name or 'No name'}) - {len(self.account_service.get_customer_accounts(c))} accounts"
                for c in customers
            ]
            
            customer_index = self.ui.select_option(customer_options, "Select customer to remove")
            if customer_index < 0:
                return
            
            selected_customer = customers[customer_index]
            
            # Check for account balances
            accounts = self.account_service.get_customer_accounts(selected_customer)
            total_balance = sum(acc.getBalance() for acc in accounts)
            
            if total_balance > 0:
                self.ui.display_message(
                    f"Cannot remove customer with non-zero balance: {self.settings.format_currency(total_balance)}", 
                    "error"
                )
                self.ui.display_message("Please ensure all account balances are zero before removal.", "info")
                return
            
            # Confirm removal
            if not self.ui.confirm(
                f"Are you sure you want to remove customer '{selected_customer.username}'? "
                f"This will also delete {len(accounts)} account(s)."
            ):
                self.ui.display_message("Customer removal cancelled.", "info")
                return
            
            # Remove customer
            success = self.user_service.delete_customer(selected_customer.userId)
            
            if success:
                self.ui.display_message(f"Customer {selected_customer.username} removed successfully!", "success")
            else:
                self.ui.display_message("Failed to remove customer.", "error")
        
        except Exception as e:
            self.ui.display_message(f"Error removing customer: {str(e)}", "error")
    
    def _view_customer_details(self) -> None:
        """View detailed information about a specific customer."""
        try:
            customers = self.user_service.get_all_customers()
            
            if not customers:
                self.ui.display_message("No customers found.", "error")
                return
            
            # Select customer
            customer_options = [f"{c.username} ({c.full_name or 'No name'})" for c in customers]
            customer_index = self.ui.select_option(customer_options, "Select customer to view")
            
            if customer_index < 0:
                return
            
            selected_customer = customers[customer_index]
            
            # Display customer information
            if hasattr(self.ui, 'display_user_info'):
                self.ui.display_user_info(selected_customer)
            else:
                headers = ["Property", "Value"]
                rows = [
                    ["Username", selected_customer.username],
                    ["Full Name", selected_customer.full_name or "Not set"],
                    ["Email", selected_customer.email or "Not set"],
                    ["Customer Since", selected_customer.customer_since.strftime("%Y-%m-%d")],
                    ["Last Login", selected_customer.last_login.strftime("%Y-%m-%d %H:%M:%S") if selected_customer.last_login else "Never"],
                    ["Status", "Active" if selected_customer.is_active else "Inactive"]
                ]
                
                self.ui.display_table(headers, rows, f"Customer Details - {selected_customer.username}")
            
            # Display account information
            accounts = self.account_service.get_customer_accounts(selected_customer)
            
            if accounts:
                headers = ["Account Number", "Type", "Balance", "Status", "Transactions"]
                rows = []
                total_balance = 0
                
                for account in accounts:
                    balance = account.getBalance()
                    total_balance += balance
                    rows.append([
                        account.accountNumber,
                        account.getType(),
                        self.settings.format_currency(balance),
                        "Active" if account.is_active else "Inactive",
                        str(len(account.transactions))
                    ])
                
                self.ui.display_table(headers, rows, "Customer Accounts")
                self.ui.display_message(
                    f"Total Balance: {self.settings.format_currency(total_balance)}", 
                    "info"
                )
            else:
                self.ui.display_message("Customer has no accounts.", "info")
        
        except Exception as e:
            self.ui.display_message(f"Error viewing customer details: {str(e)}", "error")
    
    def _view_system_statistics(self) -> None:
        """View system-wide statistics."""
        try:
            stats = self.user_service.get_system_statistics()
            
            if hasattr(self.ui, 'display_quick_stats'):
                formatted_stats = {
                    "Total Users": stats["total_users"],
                    "Customers": stats["total_customers"],
                    "Managers": stats["total_managers"],
                    "Active Users": stats["active_users"],
                    "Total Accounts": stats["total_accounts"],
                    "Active Accounts": stats["active_accounts"],
                    "System Balance": stats["total_system_balance"]
                }
                self.ui.display_quick_stats(formatted_stats)
            else:
                headers = ["Metric", "Value"]
                rows = [
                    ["Total Users", str(stats["total_users"])],
                    ["Total Customers", str(stats["total_customers"])],
                    ["Total Managers", str(stats["total_managers"])],
                    ["Active Users", str(stats["active_users"])],
                    ["Total Accounts", str(stats["total_accounts"])],
                    ["Active Accounts", str(stats["active_accounts"])],
                    ["Total System Balance", self.settings.format_currency(stats["total_system_balance"])]
                ]
                
                self.ui.display_table(headers, rows, "System Statistics")
            
            # Display account type breakdown
            if stats["account_types"]:
                headers = ["Account Type", "Count", "Total Balance"]
                rows = []
                
                for acc_type, type_stats in stats["account_types"].items():
                    rows.append([
                        acc_type,
                        str(type_stats["count"]),
                        self.settings.format_currency(type_stats["balance"])
                    ])
                
                self.ui.display_table(headers, rows, "Account Types Breakdown")
        
        except Exception as e:
            self.ui.display_message(f"Error viewing statistics: {str(e)}", "error")
    
    def _account_management(self) -> None:
        """Account management operations."""
        try:
            options = [
                "Activate Account",
                "Deactivate Account",
                "View All Accounts",
                "Search Accounts",
                "Back to Main Menu"
            ]
            
            choice = self.ui.select_option(options, "Account Management")
            
            if choice == 0:
                self._activate_account()
            elif choice == 1:
                self._deactivate_account()
            elif choice == 2:
                self._view_all_accounts()
            elif choice == 3:
                self._search_accounts()
            # choice == 4 returns to main menu
        
        except Exception as e:
            self.ui.display_message(f"Error in account management: {str(e)}", "error")
    
    def _activate_account(self) -> None:
        """Activate an inactive account."""
        try:
            inactive_accounts = self.account_service.get_inactive_accounts()
            
            if not inactive_accounts:
                self.ui.display_message("No inactive accounts found.", "info")
                return
            
            # Select account to activate
            account_options = [
                f"{acc.accountNumber} ({acc.getType()}) - Owner: {acc.owner_id[:8]}..."
                for acc in inactive_accounts
            ]
            
            account_index = self.ui.select_option(account_options, "Select account to activate")
            if account_index < 0:
                return
            
            selected_account = inactive_accounts[account_index]
            
            if self.ui.confirm(f"Activate account {selected_account.accountNumber}?"):
                success = self.account_service.activate_account(selected_account.accountNumber)
                
                if success:
                    self.ui.display_message(f"Account {selected_account.accountNumber} activated successfully!", "success")
                else:
                    self.ui.display_message("Failed to activate account.", "error")
        
        except Exception as e:
            self.ui.display_message(f"Error activating account: {str(e)}", "error")
    
    def _deactivate_account(self) -> None:
        """Deactivate an active account."""
        try:
            active_accounts = self.account_service.get_active_accounts()
            
            if not active_accounts:
                self.ui.display_message("No active accounts found.", "info")
                return
            
            # Select account to deactivate
            account_options = [
                f"{acc.accountNumber} ({acc.getType()}) - Balance: {self.settings.format_currency(acc.getBalance())}"
                for acc in active_accounts
            ]
            
            account_index = self.ui.select_option(account_options, "Select account to deactivate")
            if account_index < 0:
                return
            
            selected_account = active_accounts[account_index]
            
            if selected_account.getBalance() > 0:
                self.ui.display_message(
                    f"Cannot deactivate account with balance: {self.settings.format_currency(selected_account.getBalance())}", 
                    "error"
                )
                return
            
            if self.ui.confirm(f"Deactivate account {selected_account.accountNumber}?"):
                success = self.account_service.deactivate_account(selected_account.accountNumber)
                
                if success:
                    self.ui.display_message(f"Account {selected_account.accountNumber} deactivated successfully!", "success")
                else:
                    self.ui.display_message("Failed to deactivate account.", "error")
        
        except Exception as e:
            self.ui.display_message(f"Error deactivating account: {str(e)}", "error")
    
    def _view_all_accounts(self) -> None:
        """View all accounts in the system."""
        try:
            all_accounts = self.account_service.get_active_accounts() + self.account_service.get_inactive_accounts()
            
            if all_accounts:
                headers = ["Account Number", "Type", "Balance", "Status", "Owner", "Transactions"]
                rows = []
                
                for account in all_accounts:
                    # Get owner username
                    owner = self.user_service.get_user_by_id(account.owner_id)
                    owner_name = owner.username if owner else "Unknown"
                    
                    rows.append([
                        account.accountNumber,
                        account.getType(),
                        self.settings.format_currency(account.getBalance()),
                        "Active" if account.is_active else "Inactive",
                        owner_name,
                        str(len(account.transactions))
                    ])
                
                self.ui.display_table(headers, rows, f"All Accounts ({len(all_accounts)} total)")
                
                # Summary statistics
                total_balance = sum(acc.getBalance() for acc in all_accounts)
                active_count = len([acc for acc in all_accounts if acc.is_active])
                
                self.ui.display_message(
                    f"Active: {active_count}/{len(all_accounts)} | "
                    f"Total Balance: {self.settings.format_currency(total_balance)}", 
                    "info"
                )
            else:
                self.ui.display_message("No accounts found.", "info")
        
        except Exception as e:
            self.ui.display_message(f"Error viewing accounts: {str(e)}", "error")
    
    def _search_accounts(self) -> None:
        """Search for accounts by various criteria."""
        try:
            search_options = [
                "Search by Account Number",
                "Search by Owner Username",
                "Search by Account Type",
                "Search by Balance Range"
            ]
            
            search_choice = self.ui.select_option(search_options, "Search Accounts")
            
            if search_choice == 0:
                account_number = self.ui.prompt("Enter account number: ")
                account = self.account_service.get_account(account_number)
                if account:
                    self._display_single_account(account)
                else:
                    self.ui.display_message("Account not found.", "info")
            
            elif search_choice == 1:
                username = self.ui.prompt("Enter owner username: ")
                user = self.user_service.get_user_by_username(username)
                if user and isinstance(user, Customer):
                    accounts = self.account_service.get_customer_accounts(user)
                    self._display_account_list(accounts, f"Accounts for {username}")
                else:
                    self.ui.display_message("Customer not found.", "info")
            
            elif search_choice == 2:
                account_types = ["Savings", "Checking", "Business"]
                type_index = self.ui.select_option(account_types, "Select account type")
                if type_index >= 0:
                    accounts = self.account_service.get_accounts_by_type(account_types[type_index])
                    self._display_account_list(accounts, f"{account_types[type_index]} Accounts")
            
            elif search_choice == 3:
                min_balance = self.ui.get_float_input("Enter minimum balance: $", 0.0)
                max_balance = self.ui.get_float_input("Enter maximum balance: $", min_balance)
                
                all_accounts = self.account_service.get_active_accounts() + self.account_service.get_inactive_accounts()
                matching_accounts = [
                    acc for acc in all_accounts 
                    if min_balance <= acc.getBalance() <= max_balance
                ]
                
                self._display_account_list(
                    matching_accounts, 
                    f"Accounts with balance ${min_balance:.2f} - ${max_balance:.2f}"
                )
        
        except Exception as e:
            self.ui.display_message(f"Error searching accounts: {str(e)}", "error")
    
    def _display_single_account(self, account) -> None:
        """Display detailed information for a single account."""
        if hasattr(self.ui, 'display_account_info'):
            self.ui.display_account_info(account)
        else:
            headers = ["Property", "Value"]
            rows = [
                ["Account Number", account.accountNumber],
                ["Type", account.getType()],
                ["Balance", self.settings.format_currency(account.getBalance())],
                ["Status", "Active" if account.is_active else "Inactive"],
                ["Owner ID", account.owner_id],
                ["Total Transactions", str(len(account.transactions))]
            ]
            
            self.ui.display_table(headers, rows, "Account Details")
    
    def _display_account_list(self, accounts: List, title: str) -> None:
        """Display a list of accounts."""
        if accounts:
            headers = ["Account Number", "Type", "Balance", "Status", "Transactions"]
            rows = []
            
            for account in accounts:
                rows.append([
                    account.accountNumber,
                    account.getType(),
                    self.settings.format_currency(account.getBalance()),
                    "Active" if account.is_active else "Inactive",
                    str(len(account.transactions))
                ])
            
            self.ui.display_table(headers, rows, f"{title} ({len(accounts)} found)")
        else:
            self.ui.display_message("No accounts found matching the criteria.", "info")
    
    def _generate_reports(self) -> None:
        """Generate various reports."""
        try:
            report_options = [
                "Customer Summary Report",
                "Account Balance Report",
                "Transaction Volume Report",
                "System Health Report"
            ]
            
            report_choice = self.ui.select_option(report_options, "Generate Reports")
            
            if report_choice == 0:
                self._generate_customer_summary_report()
            elif report_choice == 1:
                self._generate_account_balance_report()
            elif report_choice == 2:
                self._generate_transaction_volume_report()
            elif report_choice == 3:
                self._generate_system_health_report()
        
        except Exception as e:
            self.ui.display_message(f"Error generating report: {str(e)}", "error")
    
    def _generate_customer_summary_report(self) -> None:
        """Generate customer summary report."""
        customers = self.user_service.get_all_customers()
        
        headers = ["Username", "Full Name", "Accounts", "Total Balance", "Last Login"]
        rows = []
        
        for customer in customers:
            accounts = self.account_service.get_customer_accounts(customer)
            total_balance = sum(acc.getBalance() for acc in accounts)
            last_login = customer.last_login.strftime("%Y-%m-%d") if customer.last_login else "Never"
            
            rows.append([
                customer.username,
                customer.full_name or "Not set",
                str(len(accounts)),
                self.settings.format_currency(total_balance),
                last_login
            ])
        
        self.ui.display_table(headers, rows, "Customer Summary Report")
    
    def _generate_account_balance_report(self) -> None:
        """Generate account balance report."""
        all_accounts = self.account_service.get_active_accounts()
        
        # Group by account type
        account_types = {}
        for account in all_accounts:
            acc_type = account.getType()
            if acc_type not in account_types:
                account_types[acc_type] = {"count": 0, "total_balance": 0.0, "accounts": []}
            
            account_types[acc_type]["count"] += 1
            account_types[acc_type]["total_balance"] += account.getBalance()
            account_types[acc_type]["accounts"].append(account)
        
        headers = ["Account Type", "Count", "Total Balance", "Average Balance"]
        rows = []
        
        for acc_type, data in account_types.items():
            avg_balance = data["total_balance"] / data["count"] if data["count"] > 0 else 0
            rows.append([
                acc_type,
                str(data["count"]),
                self.settings.format_currency(data["total_balance"]),
                self.settings.format_currency(avg_balance)
            ])
        
        self.ui.display_table(headers, rows, "Account Balance Report")
    
    def _generate_transaction_volume_report(self) -> None:
        """Generate transaction volume report."""
        all_accounts = self.account_service.get_active_accounts() + self.account_service.get_inactive_accounts()
        
        total_transactions = 0
        transaction_types = {}
        
        for account in all_accounts:
            total_transactions += len(account.transactions)
            
            for transaction in account.transactions:
                trans_type = transaction.type
                if trans_type not in transaction_types:
                    transaction_types[trans_type] = {"count": 0, "total_amount": 0.0}
                
                transaction_types[trans_type]["count"] += 1
                transaction_types[trans_type]["total_amount"] += transaction.amount
        
        self.ui.display_message(f"Total Transactions: {total_transactions}", "info")
        
        if transaction_types:
            headers = ["Transaction Type", "Count", "Total Amount", "Average Amount"]
            rows = []
            
            for trans_type, data in transaction_types.items():
                avg_amount = data["total_amount"] / data["count"] if data["count"] > 0 else 0
                rows.append([
                    trans_type,
                    str(data["count"]),
                    self.settings.format_currency(data["total_amount"]),
                    self.settings.format_currency(avg_amount)
                ])
            
            self.ui.display_table(headers, rows, "Transaction Volume Report")
        else:
            self.ui.display_message("No transactions found.", "info")
    
    def _generate_system_health_report(self) -> None:
        """Generate system health report."""
        stats = self.user_service.get_system_statistics()
        
        # Calculate health metrics
        total_users = stats["total_users"]
        active_users = stats["active_users"]
        user_activity_rate = (active_users / total_users * 100) if total_users > 0 else 0
        
        total_accounts = stats["total_accounts"]
        active_accounts = stats["active_accounts"]
        account_activity_rate = (active_accounts / total_accounts * 100) if total_accounts > 0 else 0
        
        headers = ["Health Metric", "Value", "Status"]
        rows = [
            ["Total Users", str(total_users), "✅" if total_users > 0 else "⚠️"],
            ["User Activity Rate", f"{user_activity_rate:.1f}%", "✅" if user_activity_rate >= 80 else "⚠️"],
            ["Total Accounts", str(total_accounts), "✅" if total_accounts > 0 else "⚠️"],
            ["Account Activity Rate", f"{account_activity_rate:.1f}%", "✅" if account_activity_rate >= 90 else "⚠️"],
            ["System Balance", self.settings.format_currency(stats["total_system_balance"]), "✅"],
            ["Active Sessions", str(self.auth_service.get_active_session_count()), "✅"]
        ]
        
        self.ui.display_table(headers, rows, "System Health Report")
    
    def _create_customer_account(self, customer: Customer) -> None:
        """Create an account for a customer (helper method)."""
        try:
            from ..models.account import Account
            
            # Get account type
            account_types = [Account.SAVINGS, Account.CHECKING, Account.BUSINESS]
            type_index = self.ui.select_option(account_types, "Select account type")
            if type_index < 0:
                return
            
            account_type = account_types[type_index]
            
            # Get initial deposit
            min_balance = self.settings.get_minimum_balance(account_type)
            initial_deposit = self.ui.get_float_input(
                f"Enter initial deposit (minimum ${min_balance:.2f}): $", 
                min_balance
            )
            
            # Create account
            account = self.account_service.create_account(
                customer=customer,
                account_type=account_type,
                initial_deposit=initial_deposit
            )
            
            self.ui.display_message(
                f"Account #{account.accountNumber} created for {customer.username}!", 
                "success"
            )
        
        except Exception as e:
            self.ui.display_message(f"Error creating account: {str(e)}", "error")
    
    def _view_profile(self) -> None:
        """View manager profile information."""
        try:
            if hasattr(self.ui, 'display_user_info'):
                self.ui.display_user_info(self.manager)
            else:
                headers = ["Property", "Value"]
                rows = [
                    ["Username", self.manager.username],
                    ["Full Name", self.manager.full_name or "Not set"],
                    ["Employee ID", self.manager.employeeId],
                    ["Department", self.manager.department],
                    ["Email", self.manager.email or "Not set"],
                    ["Hire Date", self.manager.hire_date.strftime("%Y-%m-%d")],
                    ["Last Login", self.manager.last_login.strftime("%Y-%m-%d %H:%M:%S") if self.manager.last_login else "Never"],
                    ["Status", "Active" if self.manager.is_active else "Inactive"]
                ]
                
                self.ui.display_table(headers, rows, "Manager Profile")
            
            # Display permissions
            headers = ["Permission", "Status"]
            rows = [[perm, "✅ Granted"] for perm in self.manager.permissions]
            
            self.ui.display_table(headers, rows, "Manager Permissions")
        
        except Exception as e:
            self.ui.display_message(f"Error viewing profile: {str(e)}", "error")