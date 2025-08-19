"""
Main DeskBank application controller.
"""

from typing import Optional
import os
import sys

from .config.settings import Settings
from .config.database_config import DatabaseConfig
from .repositories.user_repository import UserRepository
from .repositories.account_repository import AccountRepository
from .services.authentication_service import AuthenticationService
from .services.transaction_service import TransactionService
from .services.account_service import AccountService
from .services.user_service import UserService
from .ui.cli import CLI
from .ui.gui import GUI
from .models.user import Manager
from .utils.validators import Validators
from .utils.formatters import Formatters


class DeskBankApp:
    """Main DeskBank application controller."""
    
    def __init__(self, ui_type: str = "CLI", config_file: Optional[str] = None):
        """
        Initialize the DeskBank application.
        
        Args:
            ui_type: Type of UI to use (CLI or GUI)
            config_file: Optional configuration file path
        """
        # Initialize configuration
        self.settings = Settings(config_file)
        self.db_config = DatabaseConfig(self.settings)
        
        # Validate configuration
        is_valid, error_msg = self.db_config.validate_configuration()
        if not is_valid:
            print(f"Configuration error: {error_msg}")
            sys.exit(1)
        
        # Initialize repositories
        self._init_repositories()
        
        # Initialize services
        self._init_services()
        
        # Initialize UI
        self._init_ui(ui_type)
        
        # Initialize default data
        self._init_default_data()
        
        # Current session
        self.current_user = None
        self.current_session_token: Optional[str] = None
        
        print("DeskBank Application initialized successfully!")
    
    def _init_repositories(self) -> None:
        """Initialize data repositories."""
        user_data_file = self.db_config.get_user_data_file()
        account_data_file = self.db_config.get_account_data_file()
        
        self.user_repository = UserRepository(user_data_file)
        self.account_repository = AccountRepository(account_data_file)
    
    def _init_services(self) -> None:
        """Initialize business services."""
        self.auth_service = AuthenticationService(self.user_repository)
        self.transaction_service = TransactionService(self.account_repository)
        self.account_service = AccountService(self.account_repository)
        self.user_service = UserService(self.user_repository, self.account_repository)
    
    def _init_ui(self, ui_type: str) -> None:
        """Initialize user interface."""
        ui_type = ui_type.upper()
        
        if ui_type == "CLI":
            self.ui = CLI()
        elif ui_type == "GUI":
            if self.settings.is_feature_enabled("gui"):
                self.ui = GUI()
            else:
                print("GUI is not enabled in configuration. Falling back to CLI.")
                self.ui = CLI()
        else:
            print(f"Unknown UI type: {ui_type}. Using CLI.")
            self.ui = CLI()
    
    def _init_default_data(self) -> None:
        """Initialize default data if needed."""
        # Create default manager if no users exist
        if self.user_repository.count() == 0:
            try:
                default_manager = self.user_service.create_manager(
                    username="admin",
                    password="admin123",
                    employee_id="MGR001",
                    full_name="System Administrator",
                    department="IT Administration"
                )
                print(f"Created default manager: {default_manager.username}")
            except Exception as e:
                print(f"Warning: Could not create default manager: {e}")
    
    def run(self) -> None:
        """Run the main application loop."""
        try:
            if hasattr(self.ui, 'display_welcome_banner'):
                self.ui.display_welcome_banner()
            
            while True:
                self.ui.display_login_screen()
                choice = self.ui.prompt("Enter your choice: ")
                
                if choice == "1":
                    self._handle_customer_login()
                elif choice == "2":
                    self._handle_manager_login()
                elif choice == "3":
                    self._handle_customer_registration()
                elif choice == "4":
                    self._handle_exit()
                    break
                else:
                    self.ui.display_message("Invalid choice. Please try again.", "error")
        
        except KeyboardInterrupt:
            self.ui.display_message("\nApplication interrupted by user.", "info")
        except Exception as e:
            self.ui.display_message(f"An unexpected error occurred: {str(e)}", "error")
        finally:
            self._cleanup()
    
    def _handle_customer_login(self) -> None:
        """Handle customer login process."""
        try:
            username = self.ui.prompt("Enter username: ")
            password = self.ui.prompt("Enter password: ", secure=True)
            
            user = self.auth_service.authenticate_user(username, password)
            
            if user and self.auth_service.is_customer(user):
                customer = self.auth_service.require_customer(user)
                self.current_user = customer
                self.current_session_token = self.auth_service.create_session(customer)
                
                self.ui.display_message(f"Welcome, {customer.full_name}!", "success")
                self._customer_menu(customer)
            else:
                self.ui.display_message("Invalid credentials or not a customer account.", "error")
        
        except Exception as e:
            self.ui.display_message(f"Login error: {str(e)}", "error")
    
    def _handle_manager_login(self) -> None:
        """Handle manager login process."""
        try:
            username = self.ui.prompt("Enter username: ")
            password = self.ui.prompt("Enter password: ", secure=True)
            
            user = self.auth_service.authenticate_user(username, password)
            
            if user and self.auth_service.is_manager(user):
                manager = self.auth_service.require_manager(user)
                self.current_user = manager
                self.current_session_token = self.auth_service.create_session(manager)
                
                self.ui.display_message(f"Welcome, {manager.full_name}!", "success")
                self._manager_menu(manager)
            else:
                self.ui.display_message("Invalid credentials or not a manager account.", "error")
        
        except Exception as e:
            self.ui.display_message(f"Login error: {str(e)}", "error")
    
    def _handle_customer_registration(self) -> None:
        """Handle customer registration process."""
        try:
            self.ui.display_message("Customer Registration", "info")
            
            # Get and validate username
            while True:
                username = self.ui.prompt("Enter username: ")
                is_valid, message = Validators.validate_username(username)
                if is_valid and not self.user_repository.username_exists(username):
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
            
            self.ui.display_message(f"Customer {username} registered successfully!", "success")
            
        except Exception as e:
            self.ui.display_message(f"Registration error: {str(e)}", "error")
    
    def _handle_exit(self) -> None:
        """Handle application exit."""
        if self.current_session_token:
            self.auth_service.logout(self.current_session_token)
        
        self.ui.display_message("Thank you for using DeskBank!", "info")
    
    def _customer_menu(self, customer) -> None:
        """Handle customer menu interactions."""
        from .controllers.customer_controller import CustomerController
        
        controller = CustomerController(
            customer=customer,
            ui=self.ui,
            account_service=self.account_service,
            transaction_service=self.transaction_service,
            user_service=self.user_service,
            settings=self.settings
        )
        
        controller.run()
        
        # Clear session when menu exits
        if self.current_session_token:
            self.auth_service.logout(self.current_session_token)
        self.current_user = None
        self.current_session_token = None
    
    def _manager_menu(self, manager) -> None:
        """Handle manager menu interactions."""
        from .controllers.manager_controller import ManagerController
        
        controller = ManagerController(
            manager=manager,
            ui=self.ui,
            user_service=self.user_service,
            account_service=self.account_service,
            transaction_service=self.transaction_service,
            auth_service=self.auth_service,
            settings=self.settings
        )
        
        controller.run()
        
        # Clear session when menu exits
        if self.current_session_token:
            self.auth_service.logout(self.current_session_token)
        self.current_user = None
        self.current_session_token = None
    
    def _cleanup(self) -> None:
        """Perform cleanup operations."""
        # Save data
        try:
            self.user_repository.save_data()
            self.account_repository.save_data()
        except Exception as e:
            print(f"Warning: Could not save data: {e}")
        
        # Cleanup expired sessions
        try:
            expired_count = self.auth_service.cleanup_expired_sessions()
            if expired_count > 0:
                print(f"Cleaned up {expired_count} expired sessions")
        except Exception:
            pass
        
        print("Application cleanup completed.")
    
    def get_system_info(self) -> dict:
        """
        Get system information.
        
        Returns:
            Dictionary with system information
        """
        return {
            "app_name": self.settings.get("app_name"),
            "app_version": self.settings.get("app_version"),
            "ui_type": self.ui.__class__.__name__,
            "data_directory": self.db_config.get_data_directory(),
            "total_users": self.user_repository.count(),
            "total_accounts": self.account_repository.count(),
            "active_sessions": self.auth_service.get_active_session_count()
        }