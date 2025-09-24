from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import pandas as pd

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def authenticate_user(email: str, password: str):
    """Authenticate a user by email and password."""
    import os
    try:
        # Get the directory of this file (backend directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'users.csv')
        users_df = pd.read_csv(csv_path)
        user = users_df[users_df['email'] == email]
        
        if user.empty:
            return False
            
        user_data = user.iloc[0]
        # Use plain text password comparison (as provided in the case)
        if password == user_data['password']:
            return {
                'email': user_data['email'],
                'name': user_data['name'],
                'role': user_data['role']
            }
        return False
    except Exception:
        return False

def get_user_by_email(email: str):
    """Get user information by email."""
    import os
    try:
        # Get the directory of this file (backend directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'users.csv')
        users_df = pd.read_csv(csv_path)
        user = users_df[users_df['email'] == email]
        
        if user.empty:
            return None
            
        user_data = user.iloc[0]
        return {
            'email': user_data['email'],
            'name': user_data['name'],
            'role': user_data['role']
        }
    except Exception:
        return None