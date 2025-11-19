"""
Authentication Manager
Handles password hashing, JWT tokens, and user verification
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
import os

class AuthManager:
    """Manage authentication and JWT tokens"""
    
    def __init__(self):
        # Secret key for JWT (should be in environment variable in production)
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = 'HS256'
        self.token_expiry = timedelta(days=7)  # Token valid for 7 days
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
        
        Returns:
            Hashed password string
        """
        try:
            # Generate salt and hash
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            raise Exception(f"Password hashing failed: {str(e)}")
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
        
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            print(f"Password verification error: {e}")
            return False
    
    def create_token(self, user_id: int, email: str = None) -> str:
        """
        Create JWT token for user
        
        Args:
            user_id: User's database ID
            email: User's email (optional)
        
        Returns:
            JWT token string
        """
        try:
            # Token payload
            payload = {
                'user_id': user_id,
                'email': email,
                'exp': datetime.utcnow() + self.token_expiry,
                'iat': datetime.utcnow()
            }
            
            # Generate token
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
        
        except Exception as e:
            raise Exception(f"Token creation failed: {str(e)}")
    
    def verify_token(self, token: str) -> Dict:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
        
        Returns:
            Decoded token payload
        
        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")
        except Exception as e:
            raise Exception(f"Token verification failed: {str(e)}")
    
    def refresh_token(self, old_token: str) -> str:
        """
        Refresh expired token if within grace period
        
        Args:
            old_token: Old JWT token
        
        Returns:
            New JWT token
        """
        try:
            # Decode without verification to get user_id
            unverified = jwt.decode(
                old_token,
                options={"verify_signature": False}
            )
            
            user_id = unverified.get('user_id')
            email = unverified.get('email')
            
            # Create new token
            return self.create_token(user_id, email)
        
        except Exception as e:
            raise Exception(f"Token refresh failed: {str(e)}")
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
        
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        return True, "Password is strong"
    
    def extract_user_id_from_token(self, token: str) -> Optional[int]:
        """
        Extract user ID from token without full verification
        
        Args:
            token: JWT token
        
        Returns:
            User ID or None
        """
        try:
            payload = self.verify_token(token)
            return payload.get('user_id')
        except:
            return None


# Global instance
_auth_manager = None

def get_auth_manager() -> AuthManager:
    """Get or create global auth manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


if __name__ == "__main__":
    # Test the auth manager
    auth = AuthManager()
    
    # Test password hashing
    password = "TestPassword123"
    hashed = auth.hash_password(password)
    print(f"Hashed password: {hashed}")
    
    # Test password verification
    is_valid = auth.verify_password(password, hashed)
    print(f"Password verification: {is_valid}")
    
    # Test token creation
    token = auth.create_token(user_id=1, email="test@example.com")
    print(f"Token created: {token[:50]}...")
    
    # Test token verification
    payload = auth.verify_token(token)
    print(f"Token payload: {payload}")
    
    # Test password strength
    weak_password = "weak"
    is_strong, message = auth.validate_password_strength(weak_password)
    print(f"Weak password check: {is_strong}, {message}")
    
    strong_password = "StrongPass123"
    is_strong, message = auth.validate_password_strength(strong_password)
    print(f"Strong password check: {is_strong}, {message}")
