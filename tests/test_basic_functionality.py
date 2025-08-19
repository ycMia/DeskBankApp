#!/usr/bin/env python3
"""
Basic functionality tests for DeskBank application.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from deskbank.models.user import Customer, Manager
from deskbank.models.account import Account
from deskbank.models.transaction import Transaction
from deskbank.repositories.user_repository import UserRepository
from deskbank.repositories.account_repository import AccountRepository
from deskbank.services.authentication_service import AuthenticationService
from deskbank.services.transaction_service import TransactionService
from deskbank.services.account_service import AccountService
from deskbank.services.user_service import UserService
from deskbank.config.settings import Settings
from deskbank.utils.validators import Validators


def test_models():
    """Test basic model functionality."""
    print("🧪 Testing Models...")
    
    # Test Transaction
    transaction = Transaction("Deposit", 100.0, "ACC123")
    assert transaction.type == "Deposit"
    assert transaction.amount == 100.0
    assert transaction.account_number == "ACC123"
    print("   ✓ Transaction model working")
    
    # Test Account
    account = Account(500.0, "Savings")
    assert account.getBalance() == 500.0
    assert account.getType() == "Savings"
    assert len(account.accountNumber) == 8
    print("   ✓ Account model working")
    
    # Test deposit
    deposit_transaction = account.deposit(200.0)
    assert account.getBalance() == 700.0
    assert len(account.transactions) == 1
    print("   ✓ Account deposit working")
    
    # Test withdrawal
    withdrawal_transaction = account.withdraw(150.0)
    assert account.getBalance() == 550.0
    assert len(account.transactions) == 2
    print("   ✓ Account withdrawal working")
    
    # Test User models
    customer = Customer("john_doe", "password123", "john@example.com", "John Doe")
    assert customer.username == "john_doe"
    assert customer.verify_password("password123")
    assert not customer.verify_password("wrong_password")
    print("   ✓ Customer model working")
    
    manager = Manager("admin", "admin123", "MGR001", "admin@bank.com", "Administrator")
    assert manager.username == "admin"
    assert manager.employeeId == "MGR001"
    assert manager.verify_password("admin123")
    print("   ✓ Manager model working")


def test_repositories():
    """Test repository functionality."""
    print("\n🧪 Testing Repositories...")
    
    # Test UserRepository
    user_repo = UserRepository()
    
    customer = Customer("test_customer", "password123")
    user_repo.add(customer)
    
    found_customer = user_repo.find_by_username("test_customer")
    assert found_customer is not None
    assert found_customer.username == "test_customer"
    print("   ✓ UserRepository working")
    
    # Test AccountRepository
    account_repo = AccountRepository()
    
    account = Account(1000.0, "Checking")
    account.owner_id = customer.userId
    account_repo.add(account)
    
    found_account = account_repo.find_by_account_number(account.accountNumber)
    assert found_account is not None
    assert found_account.getBalance() == 1000.0
    print("   ✓ AccountRepository working")


def test_services():
    """Test service functionality."""
    print("\n🧪 Testing Services...")
    
    # Setup repositories
    user_repo = UserRepository()
    account_repo = AccountRepository()
    
    # Test AuthenticationService
    auth_service = AuthenticationService(user_repo)
    
    customer = Customer("test_user", "password123")
    user_repo.add(customer)
    
    authenticated_user = auth_service.authenticate_user("test_user", "password123")
    assert authenticated_user is not None
    assert authenticated_user.username == "test_user"
    
    # Test wrong password
    wrong_auth = auth_service.authenticate_user("test_user", "wrong_password")
    assert wrong_auth is None
    print("   ✓ AuthenticationService working")
    
    # Test AccountService
    account_service = AccountService(account_repo)
    
    account = account_service.create_account(customer, "Savings", 500.0)
    assert account.getBalance() == 500.0
    assert account.owner_id == customer.userId
    print("   ✓ AccountService working")
    
    # Test TransactionService
    transaction_service = TransactionService(account_repo)
    
    # Add account to repository
    account_repo.add(account)
    
    # Test deposit
    deposit_transaction = transaction_service.make_deposit(account.accountNumber, 200.0)
    assert account.getBalance() == 700.0
    assert deposit_transaction.type == "Deposit"
    print("   ✓ TransactionService deposit working")
    
    # Test withdrawal
    withdrawal_transaction = transaction_service.make_withdrawal(account.accountNumber, 100.0)
    assert account.getBalance() == 600.0
    assert withdrawal_transaction.type == "Withdrawal"
    print("   ✓ TransactionService withdrawal working")


def test_validators():
    """Test validation utilities."""
    print("\n🧪 Testing Validators...")
    
    # Test username validation
    valid, msg = Validators.validate_username("john_doe")
    assert valid
    
    invalid, msg = Validators.validate_username("j")  # Too short
    assert not invalid
    print("   ✓ Username validation working")
    
    # Test password validation
    valid, msg = Validators.validate_password("StrongPass4#7!")
    assert valid
    
    invalid, msg = Validators.validate_password("weak")  # Too weak
    assert not invalid
    print("   ✓ Password validation working")
    
    # Test email validation
    valid, msg = Validators.validate_email("user@example.com")
    assert valid
    
    invalid, msg = Validators.validate_email("invalid-email")
    assert not invalid
    print("   ✓ Email validation working")
    
    # Test amount validation
    valid, msg, amount = Validators.validate_amount("123.45")
    assert valid
    assert amount == 123.45
    
    invalid, msg, amount = Validators.validate_amount("-10")  # Negative
    assert not invalid
    print("   ✓ Amount validation working")


def test_settings():
    """Test configuration settings."""
    print("\n🧪 Testing Configuration...")
    
    settings = Settings()
    
    # Test basic settings
    app_name = settings.get("app_name")
    assert app_name == "DeskBank"
    
    # Test nested settings
    savings_limit = settings.get("daily_transaction_limits.Savings")
    assert savings_limit == 5000.0
    
    # Test currency formatting
    formatted = settings.format_currency(1234.56)
    assert "$1,234.56" in formatted
    
    # Test password policy
    valid, msg = settings.validate_password_policy("StrongPass123!")
    assert valid
    
    print("   ✓ Settings and configuration working")


def test_integration():
    """Test integration between components."""
    print("\n🧪 Testing Integration...")
    
    # Setup
    user_repo = UserRepository()
    account_repo = AccountRepository()
    auth_service = AuthenticationService(user_repo)
    account_service = AccountService(account_repo)
    transaction_service = TransactionService(account_repo)
    user_service = UserService(user_repo, account_repo)
    
    # Create customer through service
    customer = user_service.register_customer("integration_test", "Password4#7!", "test@example.com")
    assert customer.username == "integration_test"
    print("   ✓ Customer registration working")
    
    # Authenticate customer
    auth_user = auth_service.authenticate_user("integration_test", "Password4#7!")
    assert auth_user is not None
    print("   ✓ Customer authentication working")
    
    # Create account
    account = account_service.create_account(customer, "Checking", 1000.0)
    customer.add_account(account)
    account_repo.add(account)
    print("   ✓ Account creation working")
    
    # Make transactions
    deposit_tx = transaction_service.make_deposit(account.accountNumber, 500.0)
    assert account.getBalance() == 1500.0
    
    withdrawal_tx = transaction_service.make_withdrawal(account.accountNumber, 200.0)
    assert account.getBalance() == 1300.0
    print("   ✓ Transaction processing working")
    
    # Get account summary
    summary = account_service.get_account_summary(customer)
    assert summary["total_accounts"] == 1
    assert summary["total_balance"] == 1300.0
    print("   ✓ Account summary working")
    
    print("   ✓ All integration tests passed")


def run_all_tests():
    """Run all tests."""
    print("🚀 Starting DeskBank Modular Architecture Tests...\n")
    
    try:
        test_models()
        test_repositories()
        test_services()
        test_validators()
        test_settings()
        test_integration()
        
        print("\n🎉 All tests passed! The modular architecture is working correctly.")
        print("\n📋 Test Summary:")
        print("   ✅ Models: Transaction, Account, User hierarchy")
        print("   ✅ Repositories: User and Account data management")
        print("   ✅ Services: Authentication, Transaction, Account, User")
        print("   ✅ Utilities: Validators and Configuration")
        print("   ✅ Integration: End-to-end functionality")
        
        print("\n🏗️  Architecture Benefits Demonstrated:")
        print("   📦 Modular design with clear separation of concerns")
        print("   🔄 Dependency injection and inversion of control")
        print("   🧪 Testable components and services")
        print("   🔧 Configurable settings and validation")
        print("   📈 Scalable and maintainable codebase")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)