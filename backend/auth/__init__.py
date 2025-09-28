"""
Authentication module for JWT token management and user validation.
"""

from .auth import (
    authenticate_user,
    create_access_token,
    verify_token,
    get_user_by_email,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password,
    get_password_hash
)

__all__ = [
    "authenticate_user",
    "create_access_token",
    "verify_token",
    "get_user_by_email",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "verify_password",
    "get_password_hash"
]