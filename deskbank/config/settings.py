"""
Application settings and configuration.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """Application settings and configuration manager."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize settings.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file
        self._settings = self._load_default_settings()
        
        if config_file and os.path.exists(config_file):
            self._load_from_file()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default application settings."""
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        
        return {
            # Application Info
            "app_name": "DeskBank",
            "app_version": "1.0.0",
            "app_description": "Modern Banking Application",
            
            # Database Settings
            "data_directory": str(data_dir),
            "user_data_file": str(data_dir / "users.json"),
            "account_data_file": str(data_dir / "accounts.json"),
            "backup_directory": str(data_dir / "backups"),
            
            # Security Settings
            "password_min_length": 8,
            "password_require_special_chars": True,
            "password_require_numbers": True,
            "password_require_uppercase": True,
            "session_timeout_hours": 24,
            "max_login_attempts": 3,
            "lockout_duration_minutes": 15,
            
            # Transaction Settings
            "default_currency": "USD",
            "currency_symbol": "$",
            "decimal_places": 2,
            "daily_transaction_limits": {
                "Savings": 5000.0,
                "Checking": 10000.0,
                "Business": 50000.0
            },
            "minimum_balances": {
                "Savings": 100.0,
                "Checking": 50.0,
                "Business": 500.0
            },
            "transfer_fees": {
                "internal": 0.0,
                "external": 2.50
            },
            
            # UI Settings
            "default_ui": "CLI",  # CLI or GUI
            "theme": "default",
            "date_format": "%Y-%m-%d %H:%M:%S",
            "currency_format": "${:,.2f}",
            "table_max_rows": 50,
            
            # Logging Settings
            "log_level": "INFO",
            "log_file": str(project_root / "logs" / "deskbank.log"),
            "log_rotation": True,
            "log_max_size_mb": 10,
            "log_backup_count": 5,
            
            # Feature Flags
            "enable_gui": False,
            "enable_reports": True,
            "enable_backups": True,
            "enable_transaction_history": True,
            "enable_account_statements": True,
            
            # Business Rules
            "allow_negative_balance": False,
            "require_account_verification": False,
            "enable_account_interest": False,
            "interest_rates": {
                "Savings": 0.02,  # 2% annual
                "Checking": 0.005,  # 0.5% annual
                "Business": 0.015   # 1.5% annual
            },
            
            # API Settings (for future extensions)
            "api_enabled": False,
            "api_port": 8000,
            "api_host": "localhost",
            "api_rate_limit": 100,  # requests per minute
            
            # Development Settings
            "debug_mode": False,
            "test_mode": False,
            "demo_data": False
        }
    
    def _load_from_file(self) -> None:
        """Load settings from configuration file."""
        try:
            import json
            with open(self.config_file, 'r') as f:
                file_settings = json.load(f)
            
            # Update default settings with file settings
            self._settings.update(file_settings)
        except Exception as e:
            print(f"Warning: Failed to load config file {self.config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        keys = key.split('.')
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            value: Value to set
        """
        keys = key.split('.')
        setting_dict = self._settings
        
        for k in keys[:-1]:
            if k not in setting_dict:
                setting_dict[k] = {}
            setting_dict = setting_dict[k]
        
        setting_dict[keys[-1]] = value
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save current settings to file.
        
        Args:
            file_path: Path to save settings
            
        Returns:
            True if successful
        """
        try:
            import json
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings to {file_path}: {e}")
            return False
    
    def get_data_directory(self) -> str:
        """Get the data directory path."""
        data_dir = self.get("data_directory")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def get_log_directory(self) -> str:
        """Get the log directory path."""
        log_file = self.get("log_file")
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def get_backup_directory(self) -> str:
        """Get the backup directory path."""
        backup_dir = self.get("backup_directory")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir
    
    def is_feature_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.
        
        Args:
            feature: Feature name
            
        Returns:
            True if feature is enabled
        """
        return self.get(f"enable_{feature}", False)
    
    def get_currency_format(self) -> str:
        """Get currency format string."""
        return self.get("currency_format", "${:,.2f}")
    
    def format_currency(self, amount: float) -> str:
        """
        Format currency amount.
        
        Args:
            amount: Amount to format
            
        Returns:
            Formatted currency string
        """
        format_string = self.get_currency_format()
        return format_string.format(amount)
    
    def get_transaction_limit(self, account_type: str) -> float:
        """
        Get daily transaction limit for account type.
        
        Args:
            account_type: Type of account
            
        Returns:
            Daily transaction limit
        """
        limits = self.get("daily_transaction_limits", {})
        return limits.get(account_type, 1000.0)
    
    def get_minimum_balance(self, account_type: str) -> float:
        """
        Get minimum balance requirement for account type.
        
        Args:
            account_type: Type of account
            
        Returns:
            Minimum balance requirement
        """
        minimums = self.get("minimum_balances", {})
        return minimums.get(account_type, 0.0)
    
    def get_interest_rate(self, account_type: str) -> float:
        """
        Get interest rate for account type.
        
        Args:
            account_type: Type of account
            
        Returns:
            Annual interest rate
        """
        rates = self.get("interest_rates", {})
        return rates.get(account_type, 0.0)
    
    def validate_password_policy(self, password: str) -> tuple:
        """
        Validate password against policy.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        min_length = self.get("password_min_length", 8)
        require_special = self.get("password_require_special_chars", True)
        require_numbers = self.get("password_require_numbers", True)
        require_uppercase = self.get("password_require_uppercase", True)
        
        if len(password) < min_length:
            return False, f"Password must be at least {min_length} characters long"
        
        if require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if require_numbers and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Get all settings as dictionary.
        
        Returns:
            Dictionary of all settings
        """
        return self._settings.copy()
    
    def __repr__(self) -> str:
        """String representation of settings."""
        return f"Settings(config_file={self.config_file})"