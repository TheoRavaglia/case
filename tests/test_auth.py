import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from auth import authenticate_user, create_access_token, verify_token, get_password_hash
from utils import setup_initial_users

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_users():
    """Setup test users before running tests."""
    # Change to backend directory for CSV operations
    os.chdir(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    setup_initial_users()
    yield
    # Cleanup could be added here if needed

class TestAuthentication:
    def test_authenticate_valid_user(self):
        """Test authentication with valid credentials."""
        user = authenticate_user("admin@company.com", "admin123")
        assert user is not False
        assert user['email'] == "admin@company.com"
        assert user['role'] == "admin"

    def test_authenticate_invalid_email(self):
        """Test authentication with invalid email."""
        user = authenticate_user("nonexistent@company.com", "admin123")
        assert user is False

    def test_authenticate_invalid_password(self):
        """Test authentication with invalid password."""
        user = authenticate_user("admin@company.com", "wrongpassword")
        assert user is False

    def test_create_and_verify_token(self):
        """Test JWT token creation and verification."""
        test_email = "test@example.com"
        token = create_access_token(data={"sub": test_email})
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify the token
        verified_email = verify_token(token)
        assert verified_email == test_email

    def test_verify_invalid_token(self):
        """Test token verification with invalid token."""
        with pytest.raises(Exception):  # Should raise HTTPException
            verify_token("invalid.token.here")

    def test_password_hashing(self):
        """Test password hashing functionality."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50  # Bcrypt hashes are typically long

class TestLoginEndpoint:
    def test_login_success(self):
        """Test successful login endpoint."""
        response = client.post(
            "/api/login",
            json={"email": "admin@company.com", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "admin@company.com"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/login",
            json={"email": "admin@company.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        response = client.post(
            "/api/login",
            json={"email": "admin@company.com"}
        )
        
        assert response.status_code == 422  # Validation error