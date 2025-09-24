import pytest
from fastapi.testclient import TestClient
import sys
import os
import pandas as pd

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from auth import create_access_token
from services import get_filtered_metrics, apply_user_permissions
from models import MetricsFilters
from utils import setup_initial_users

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    """Setup test data before running tests."""
    # Change to backend directory for CSV operations
    os.chdir(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    setup_initial_users()
    yield

@pytest.fixture
def admin_token():
    """Create admin token for testing."""
    return create_access_token(data={"sub": "admin@company.com"})

@pytest.fixture
def user_token():
    """Create regular user token for testing."""
    return create_access_token(data={"sub": "user@company.com"})

@pytest.fixture
def sample_metrics_data():
    """Create sample metrics data for testing."""
    return pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'campaign_name': ['Campaign A', 'Campaign B', 'Campaign C'],
        'impressions': [1000, 2000, 3000],
        'clicks': [100, 200, 300],
        'cost_micros': [50000000, 100000000, 150000000],  # $50, $100, $150
        'conversions': [5.0, 10.0, 15.0],
        'conversion_rate': [0.05, 0.05, 0.05]
    })

class TestUserPermissions:
    def test_admin_sees_cost_column(self, sample_metrics_data):
        """Test that admin users can see the cost_micros column."""
        admin_user = {'email': 'admin@company.com', 'role': 'admin'}
        
        result_df = apply_user_permissions(sample_metrics_data.copy(), admin_user)
        
        assert 'cost_micros' in result_df.columns
        assert len(result_df.columns) == len(sample_metrics_data.columns)

    def test_regular_user_cannot_see_cost_column(self, sample_metrics_data):
        """Test that regular users cannot see the cost_micros column."""
        regular_user = {'email': 'user@company.com', 'role': 'user'}
        
        result_df = apply_user_permissions(sample_metrics_data.copy(), regular_user)
        
        assert 'cost_micros' not in result_df.columns
        assert len(result_df.columns) == len(sample_metrics_data.columns) - 1

    def test_admin_metrics_endpoint_includes_cost(self, admin_token):
        """Test that admin users get cost data from API endpoint."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.post(
            "/api/metrics",
            json={},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check if any metric has cost_micros (admin should see it)
        if data['metrics']:
            first_metric = data['metrics'][0]
            # Admin should have access to cost_micros field
            assert 'cost_micros' in first_metric or first_metric.get('cost_micros') is not None

    def test_regular_user_metrics_endpoint_excludes_cost(self, user_token):
        """Test that regular users don't get cost data from API endpoint."""
        headers = {"Authorization": f"Bearer {user_token}"}
        
        response = client.post(
            "/api/metrics",
            json={},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that regular user doesn't get cost_micros
        if data['metrics']:
            first_metric = data['metrics'][0]
            # Regular user should not have cost_micros field or it should be None
            assert 'cost_micros' not in first_metric or first_metric.get('cost_micros') is None

class TestUnauthorizedAccess:
    def test_metrics_endpoint_requires_auth(self):
        """Test that metrics endpoint requires authentication."""
        response = client.post("/api/metrics", json={})
        
        assert response.status_code == 401

    def test_user_info_endpoint_requires_auth(self):
        """Test that user info endpoint requires authentication."""
        response = client.get("/api/me")
        
        assert response.status_code == 401

    def test_invalid_token_rejected(self):
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        
        response = client.post("/api/metrics", json={}, headers=headers)
        
        assert response.status_code == 401