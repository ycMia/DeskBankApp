"""
Formatting utilities for DeskBank application.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal


class Formatters:
    """Collection of formatting utilities."""
    
    @staticmethod
    def format_currency(amount: float, currency_symbol: str = "$", 
                       decimal_places: int = 2) -> str:
        """
        Format currency amount.
        
        Args:
            amount: Amount to format
            currency_symbol: Currency symbol
            decimal_places: Number of decimal places
            
        Returns:
            Formatted currency string
        """
        try:
            # Use Decimal for precise formatting
            decimal_amount = Decimal(str(amount))
            format_string = f"{{:,.{decimal_places}f}}"
            formatted_number = format_string.format(float(decimal_amount))
            return f"{currency_symbol}{formatted_number}"
        except (ValueError, TypeError):
            return f"{currency_symbol}0.00"
    
    @staticmethod
    def format_percentage(value: float, decimal_places: int = 2) -> str:
        """
        Format percentage value.
        
        Args:
            value: Percentage value (0.05 for 5%)
            decimal_places: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        try:
            percentage = value * 100
            format_string = f"{{:.{decimal_places}f}}%"
            return format_string.format(percentage)
        except (ValueError, TypeError):
            return "0.00%"
    
    @staticmethod
    def format_date(date_obj: datetime, format_string: str = "%Y-%m-%d") -> str:
        """
        Format date object.
        
        Args:
            date_obj: Date object to format
            format_string: Format string
            
        Returns:
            Formatted date string
        """
        try:
            return date_obj.strftime(format_string)
        except (AttributeError, ValueError):
            return "N/A"
    
    @staticmethod
    def format_datetime(datetime_obj: datetime, 
                       format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format datetime object.
        
        Args:
            datetime_obj: Datetime object to format
            format_string: Format string
            
        Returns:
            Formatted datetime string
        """
        try:
            return datetime_obj.strftime(format_string)
        except (AttributeError, ValueError):
            return "N/A"
    
    @staticmethod
    def format_account_number(account_number: str, 
                             mask_digits: bool = False) -> str:
        """
        Format account number with optional masking.
        
        Args:
            account_number: Account number to format
            mask_digits: Whether to mask some digits for security
            
        Returns:
            Formatted account number
        """
        if not account_number:
            return "N/A"
        
        if mask_digits and len(account_number) > 4:
            # Show first 2 and last 2 characters, mask the rest
            masked = account_number[:2] + "*" * (len(account_number) - 4) + account_number[-2:]
            return masked
        
        return account_number
    
    @staticmethod
    def format_phone_number(phone: str) -> str:
        """
        Format phone number.
        
        Args:
            phone: Phone number to format
            
        Returns:
            Formatted phone number
        """
        if not phone:
            return "N/A"
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        if len(digits) == 10:
            # US format: (XXX) XXX-XXXX
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            # US format with country code: +1 (XXX) XXX-XXXX
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            # International or unknown format
            return phone
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted file size string
        """
        try:
            if size_bytes == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            size_bytes = float(size_bytes)
            i = 0
            
            while size_bytes >= 1024.0 and i < len(size_names) - 1:
                size_bytes /= 1024.0
                i += 1
            
            return f"{size_bytes:.1f} {size_names[i]}"
        except (ValueError, TypeError):
            return "0 B"
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        try:
            if seconds < 60:
                return f"{seconds} seconds"
            elif seconds < 3600:
                minutes = seconds // 60
                remaining_seconds = seconds % 60
                if remaining_seconds == 0:
                    return f"{minutes} minutes"
                else:
                    return f"{minutes} minutes, {remaining_seconds} seconds"
            elif seconds < 86400:
                hours = seconds // 3600
                remaining_minutes = (seconds % 3600) // 60
                if remaining_minutes == 0:
                    return f"{hours} hours"
                else:
                    return f"{hours} hours, {remaining_minutes} minutes"
            else:
                days = seconds // 86400
                remaining_hours = (seconds % 86400) // 3600
                if remaining_hours == 0:
                    return f"{days} days"
                else:
                    return f"{days} days, {remaining_hours} hours"
        except (ValueError, TypeError):
            return "0 seconds"
    
    @staticmethod
    def format_table_row(values: List[str], widths: List[int], 
                        separator: str = " | ") -> str:
        """
        Format table row with proper column alignment.
        
        Args:
            values: Column values
            widths: Column widths
            separator: Column separator
            
        Returns:
            Formatted table row
        """
        formatted_values = []
        for i, value in enumerate(values):
            if i < len(widths):
                width = widths[i]
                # Truncate if too long, pad if too short
                if len(value) > width:
                    formatted_value = value[:width-3] + "..."
                else:
                    formatted_value = value.ljust(width)
                formatted_values.append(formatted_value)
            else:
                formatted_values.append(value)
        
        return separator.join(formatted_values)
    
    @staticmethod
    def format_transaction_type(transaction_type: str) -> str:
        """
        Format transaction type for display.
        
        Args:
            transaction_type: Transaction type
            
        Returns:
            Formatted transaction type
        """
        type_mapping = {
            "deposit": "💰 Deposit",
            "withdrawal": "💸 Withdrawal",
            "transfer_in": "📥 Transfer In",
            "transfer_out": "📤 Transfer Out",
            "fee": "💳 Fee",
            "interest": "📈 Interest",
            "refund": "🔄 Refund"
        }
        
        return type_mapping.get(transaction_type.lower(), transaction_type)
    
    @staticmethod
    def format_account_status(is_active: bool) -> str:
        """
        Format account status for display.
        
        Args:
            is_active: Account active status
            
        Returns:
            Formatted status string
        """
        return "🟢 Active" if is_active else "🔴 Inactive"
    
    @staticmethod
    def format_user_role(user_type: str) -> str:
        """
        Format user role for display.
        
        Args:
            user_type: User type
            
        Returns:
            Formatted role string
        """
        role_mapping = {
            "customer": "👤 Customer",
            "manager": "👔 Manager",
            "admin": "👑 Administrator"
        }
        
        return role_mapping.get(user_type.lower(), user_type)
    
    @staticmethod
    def format_success_message(message: str) -> str:
        """
        Format success message.
        
        Args:
            message: Success message
            
        Returns:
            Formatted success message
        """
        return f"✅ {message}"
    
    @staticmethod
    def format_error_message(message: str) -> str:
        """
        Format error message.
        
        Args:
            message: Error message
            
        Returns:
            Formatted error message
        """
        return f"❌ {message}"
    
    @staticmethod
    def format_warning_message(message: str) -> str:
        """
        Format warning message.
        
        Args:
            message: Warning message
            
        Returns:
            Formatted warning message
        """
        return f"⚠️  {message}"
    
    @staticmethod
    def format_info_message(message: str) -> str:
        """
        Format info message.
        
        Args:
            message: Info message
            
        Returns:
            Formatted info message
        """
        return f"ℹ️  {message}"
    
    @staticmethod
    def format_menu_header(title: str, width: int = 60) -> str:
        """
        Format menu header with decorative border.
        
        Args:
            title: Menu title
            width: Total width of header
            
        Returns:
            Formatted menu header
        """
        if len(title) >= width - 4:
            return f"== {title[:width-7]}... =="
        
        padding = (width - len(title) - 4) // 2
        left_padding = "=" * padding
        right_padding = "=" * (width - len(title) - 4 - padding)
        
        return f"{left_padding} {title} {right_padding}"
    
    @staticmethod
    def format_json_pretty(data: Dict[str, Any], indent: int = 2) -> str:
        """
        Format dictionary as pretty JSON.
        
        Args:
            data: Dictionary to format
            indent: Indentation level
            
        Returns:
            Pretty formatted JSON string
        """
        import json
        try:
            return json.dumps(data, indent=indent, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(data)