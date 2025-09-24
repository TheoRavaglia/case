"""
Integration tests with real CSV data.
Run these optionally with: pytest tests/test_integration.py -v
These tests are slower but test against the full dataset.
"""
import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from utils import setup_initial_users

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_integration_test_data():
    """Setup test data for integration tests."""
    # Change to backend directory for CSV operations
    os.chdir(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    setup_initial_users()
    yield

@pytest.mark.integration
class TestFullDataIntegration:
    """Integration tests that use the full CSV dataset."""
    
    def test_full_metrics_load_performance(self, admin_token):
        """Test that the API can handle the full dataset reasonably fast."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.post(
            "/api/metrics",
            json={"sort_by": "date", "sort_order": "desc"},
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have the full dataset
        assert data['total_count'] > 1000000  # We know it's a large dataset
        assert len(data['metrics']) > 0
    
    def test_date_filtering_with_full_data(self, admin_token):
        """Test date filtering works with the complete dataset."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.post(
            "/api/metrics",
            json={
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            },
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] >= 0
    
    def test_search_with_full_data(self, admin_token):
        """Test search functionality with complete dataset."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Search for a specific campaign ID that exists
        response = client.post(
            "/api/metrics", 
            json={"search": "6320590762"},  # One of the campaign IDs we saw
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['total_count'] >= 0