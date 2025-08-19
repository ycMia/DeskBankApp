"""
Authentication service for user login and session management.
"""

from typing import Optional
from datetime import datetime, timedelta
import secrets

from ..models.user import User, Customer, Manager
from ..repositories.user_repository import UserRepository


class AuthenticationService:
    """Service for user authentication and session management."""
    
    def __init__(self, user_repository: UserRepository):
        """
        Initialize the authentication service.
        
        Args:
            user_repository: Repository for user data
        """
        self.user_repository = user_repository
        self._active_sessions = {}  # session_token -> user_id
        self._session_timeout = timedelta(hours=24)  # 24 hour session timeout
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        return self.user_repository.authenticate(username, password)
    
    def create_session(self, user: User) -> str:
        """
        Create a session for an authenticated user.
        
        Args:
            user: Authenticated user
            
        Returns:
            Session token
        """
        session_token = secrets.token_urlsafe(32)
        self._active_sessions[session_token] = {
            'user_id': user.userId,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """
        Validate a session token and return the associated user.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            User if session is valid, None otherwise
        """
        if session_token not in self._active_sessions:
            return None
        
        session = self._active_sessions[session_token]
        
        # Check if session has expired
        if datetime.now() - session['last_activity'] > self._session_timeout:
            del self._active_sessions[session_token]
            return None
        
        # Update last activity
        session['last_activity'] = datetime.now()
        
        # Get user
        user = self.user_repository.get_by_id(session['user_id'])
        if not user or not user.is_active:
            del self._active_sessions[session_token]
            return None
        
        return user
    
    def logout(self, session_token: str) -> bool:
        """
        Logout a user by invalidating their session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            True if session was found and invalidated
        """
        if session_token in self._active_sessions:
            del self._active_sessions[session_token]
            return True
        return False
    
    def logout_user(self, user_id: str) -> int:
        """
        Logout all sessions for a specific user.
        
        Args:
            user_id: User ID to logout
            
        Returns:
            Number of sessions that were invalidated
        """
        sessions_to_remove = [
            token for token, session in self._active_sessions.items()
            if session['user_id'] == user_id
        ]
        
        for token in sessions_to_remove:
            del self._active_sessions[token]
        
        return len(sessions_to_remove)
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions.
        
        Returns:
            Number of sessions that were cleaned up
        """
        current_time = datetime.now()
        expired_tokens = [
            token for token, session in self._active_sessions.items()
            if current_time - session['last_activity'] > self._session_timeout
        ]
        
        for token in expired_tokens:
            del self._active_sessions[token]
        
        return len(expired_tokens)
    
    def get_active_session_count(self) -> int:
        """
        Get the number of active sessions.
        
        Returns:
            Number of active sessions
        """
        return len(self._active_sessions)
    
    def get_user_session_count(self, user_id: str) -> int:
        """
        Get the number of active sessions for a specific user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of active sessions for the user
        """
        return sum(1 for session in self._active_sessions.values()
                  if session['user_id'] == user_id)
    
    def is_customer(self, user: User) -> bool:
        """
        Check if a user is a customer.
        
        Args:
            user: User to check
            
        Returns:
            True if user is a customer
        """
        return isinstance(user, Customer)
    
    def is_manager(self, user: User) -> bool:
        """
        Check if a user is a manager.
        
        Args:
            user: User to check
            
        Returns:
            True if user is a manager
        """
        return isinstance(user, Manager)
    
    def require_customer(self, user: User) -> Customer:
        """
        Ensure user is a customer and return as Customer type.
        
        Args:
            user: User to check
            
        Returns:
            Customer object
            
        Raises:
            ValueError: If user is not a customer
        """
        if not isinstance(user, Customer):
            raise ValueError("User must be a customer for this operation")
        return user
    
    def require_manager(self, user: User) -> Manager:
        """
        Ensure user is a manager and return as Manager type.
        
        Args:
            user: User to check
            
        Returns:
            Manager object
            
        Raises:
            ValueError: If user is not a manager
        """
        if not isinstance(user, Manager):
            raise ValueError("User must be a manager for this operation")
        return user
    
    def check_permission(self, user: User, permission: str) -> bool:
        """
        Check if a user has a specific permission.
        
        Args:
            user: User to check
            permission: Permission to check
            
        Returns:
            True if user has the permission
        """
        if isinstance(user, Manager):
            return user.has_permission(permission)
        return False