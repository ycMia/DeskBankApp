"""
Database configuration and connection settings.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


class DatabaseConfig:
    """Database configuration manager."""
    
    def __init__(self, settings: Optional['Settings'] = None):
        """
        Initialize database configuration.
        
        Args:
            settings: Application settings instance
        """
        self.settings = settings
        self._config = self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default database configuration."""
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data"
        
        # Ensure data directory exists
        data_dir.mkdir(exist_ok=True)
        
        return {
            # File-based storage (current implementation)
            "storage_type": "file",
            "data_directory": str(data_dir),
            "user_data_file": str(data_dir / "users.json"),
            "account_data_file": str(data_dir / "accounts.json"),
            "transaction_data_file": str(data_dir / "transactions.json"),
            "backup_directory": str(data_dir / "backups"),
            "auto_backup": True,
            "backup_interval_hours": 24,
            "max_backup_files": 10,
            
            # SQLite configuration (for future implementation)
            "sqlite": {
                "enabled": False,
                "database_file": str(data_dir / "deskbank.db"),
                "connection_timeout": 30,
                "enable_foreign_keys": True,
                "enable_wal_mode": True,
                "vacuum_on_startup": False
            },
            
            # PostgreSQL configuration (for future implementation)
            "postgresql": {
                "enabled": False,
                "host": "localhost",
                "port": 5432,
                "database": "deskbank",
                "username": "deskbank_user",
                "password": "",
                "connection_pool_size": 5,
                "connection_timeout": 30,
                "ssl_mode": "prefer"
            },
            
            # MySQL configuration (for future implementation)
            "mysql": {
                "enabled": False,
                "host": "localhost",
                "port": 3306,
                "database": "deskbank",
                "username": "deskbank_user",
                "password": "",
                "charset": "utf8mb4",
                "connection_pool_size": 5,
                "connection_timeout": 30
            },
            
            # Data validation settings
            "validate_data_integrity": True,
            "enable_data_encryption": False,
            "encryption_key_file": str(data_dir / ".encryption_key"),
            
            # Performance settings
            "cache_enabled": True,
            "cache_size_mb": 50,
            "cache_ttl_seconds": 3600,
            "batch_size": 100,
            
            # Logging settings
            "log_queries": False,
            "log_slow_queries": True,
            "slow_query_threshold_ms": 1000
        }
    
    def get_storage_type(self) -> str:
        """Get the configured storage type."""
        return self._config.get("storage_type", "file")
    
    def get_data_directory(self) -> str:
        """Get the data directory path."""
        if self.settings:
            return self.settings.get_data_directory()
        else:
            data_dir = self._config["data_directory"]
            os.makedirs(data_dir, exist_ok=True)
            return data_dir
    
    def get_user_data_file(self) -> str:
        """Get the user data file path."""
        if self.settings:
            return self.settings.get("user_data_file")
        else:
            return self._config["user_data_file"]
    
    def get_account_data_file(self) -> str:
        """Get the account data file path."""
        if self.settings:
            return self.settings.get("account_data_file")
        else:
            return self._config["account_data_file"]
    
    def get_backup_directory(self) -> str:
        """Get the backup directory path."""
        if self.settings:
            return self.settings.get_backup_directory()
        else:
            backup_dir = self._config["backup_directory"]
            os.makedirs(backup_dir, exist_ok=True)
            return backup_dir
    
    def is_auto_backup_enabled(self) -> bool:
        """Check if auto backup is enabled."""
        return self._config.get("auto_backup", True)
    
    def get_backup_interval(self) -> int:
        """Get backup interval in hours."""
        return self._config.get("backup_interval_hours", 24)
    
    def get_max_backup_files(self) -> int:
        """Get maximum number of backup files to keep."""
        return self._config.get("max_backup_files", 10)
    
    def is_sqlite_enabled(self) -> bool:
        """Check if SQLite is enabled."""
        return self._config.get("sqlite", {}).get("enabled", False)
    
    def get_sqlite_config(self) -> Dict[str, Any]:
        """Get SQLite configuration."""
        return self._config.get("sqlite", {})
    
    def is_postgresql_enabled(self) -> bool:
        """Check if PostgreSQL is enabled."""
        return self._config.get("postgresql", {}).get("enabled", False)
    
    def get_postgresql_config(self) -> Dict[str, Any]:
        """Get PostgreSQL configuration."""
        return self._config.get("postgresql", {})
    
    def is_mysql_enabled(self) -> bool:
        """Check if MySQL is enabled."""
        return self._config.get("mysql", {}).get("enabled", False)
    
    def get_mysql_config(self) -> Dict[str, Any]:
        """Get MySQL configuration."""
        return self._config.get("mysql", {})
    
    def is_data_validation_enabled(self) -> bool:
        """Check if data validation is enabled."""
        return self._config.get("validate_data_integrity", True)
    
    def is_encryption_enabled(self) -> bool:
        """Check if data encryption is enabled."""
        return self._config.get("enable_data_encryption", False)
    
    def get_encryption_key_file(self) -> str:
        """Get encryption key file path."""
        return self._config.get("encryption_key_file", "")
    
    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self._config.get("cache_enabled", True)
    
    def get_cache_size_mb(self) -> int:
        """Get cache size in MB."""
        return self._config.get("cache_size_mb", 50)
    
    def get_cache_ttl_seconds(self) -> int:
        """Get cache TTL in seconds."""
        return self._config.get("cache_ttl_seconds", 3600)
    
    def get_batch_size(self) -> int:
        """Get batch processing size."""
        return self._config.get("batch_size", 100)
    
    def is_query_logging_enabled(self) -> bool:
        """Check if query logging is enabled."""
        return self._config.get("log_queries", False)
    
    def is_slow_query_logging_enabled(self) -> bool:
        """Check if slow query logging is enabled."""
        return self._config.get("log_slow_queries", True)
    
    def get_slow_query_threshold_ms(self) -> int:
        """Get slow query threshold in milliseconds."""
        return self._config.get("slow_query_threshold_ms", 1000)
    
    def create_connection_string(self, db_type: str) -> str:
        """
        Create database connection string.
        
        Args:
            db_type: Database type (sqlite, postgresql, mysql)
            
        Returns:
            Connection string
        """
        if db_type == "sqlite":
            config = self.get_sqlite_config()
            return f"sqlite:///{config.get('database_file', '')}"
        
        elif db_type == "postgresql":
            config = self.get_postgresql_config()
            user = config.get('username', '')
            password = config.get('password', '')
            host = config.get('host', 'localhost')
            port = config.get('port', 5432)
            database = config.get('database', '')
            
            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
        
        elif db_type == "mysql":
            config = self.get_mysql_config()
            user = config.get('username', '')
            password = config.get('password', '')
            host = config.get('host', 'localhost')
            port = config.get('port', 3306)
            database = config.get('database', '')
            
            return f"mysql://{user}:{password}@{host}:{port}/{database}"
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def validate_configuration(self) -> tuple:
        """
        Validate database configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check data directory exists or can be created
            data_dir = self.get_data_directory()
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # Check write permissions
            test_file = os.path.join(data_dir, ".write_test")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except Exception:
                return False, f"No write permission to data directory: {data_dir}"
            
            # Check backup directory
            backup_dir = self.get_backup_directory()
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            return True, "Configuration is valid"
        
        except Exception as e:
            return False, f"Configuration validation failed: {str(e)}"
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get configuration summary.
        
        Returns:
            Dictionary with configuration summary
        """
        return {
            "storage_type": self.get_storage_type(),
            "data_directory": self.get_data_directory(),
            "auto_backup": self.is_auto_backup_enabled(),
            "backup_interval_hours": self.get_backup_interval(),
            "cache_enabled": self.is_cache_enabled(),
            "encryption_enabled": self.is_encryption_enabled(),
            "validation_enabled": self.is_data_validation_enabled()
        }