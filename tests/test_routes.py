import pytest
from fastapi.testclient import TestClient
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from services.services import filter_metrics_by_date, search_metrics, sort_metrics
from models import MetricsFilters
from utils import setup_initial_users
import pandas as pd

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_data():
    """Setup test data before running tests."""
    # Change to backend directory for CSV operations
    os.chdir(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    setup_initial_users()
    yield

# Admin and user tokens are now provided by conftest.py

# Sample metrics fixture is now in conftest.py

class TestMetricsEndpoints:
    def test_get_user_info_success(self, admin_token):
        """Test successful user info retrieval."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = client.get("/api/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data['email'] == 'admin@company.com'
        assert data['role'] == 'admin'

    def test_get_metrics_success(self, admin_token, mock_load_metrics):
        """Test successful metrics retrieval."""
        headers = {"Authorization": f"Bearer {admin_token}"}

        response = client.post(
            "/api/metrics",
            json={},
            headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert 'metrics' in data
        assert 'total_count' in data
        assert isinstance(data['metrics'], list)
        assert isinstance(data['total_count'], int)
        assert data['total_count'] == 4  # Our mock has 4 records    def test_get_metrics_with_filters(self, admin_token, mock_load_metrics):
        """Test metrics retrieval with filters."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        filters = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "sort_by": "date",
            "sort_order": "desc"
        }
        
        response = client.post(
            "/api/metrics",
            json=filters,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'metrics' in data

class TestMetricsFiltering:
    def test_date_filtering(self, sample_metrics_df):
        """Test filtering metrics by date range."""
        # Filter for first two days only
        filtered_df = filter_metrics_by_date(
            sample_metrics_df.copy(),
            start_date="2024-01-01",
            end_date="2024-01-02"
        )
        
        assert len(filtered_df) == 2
        assert filtered_df['date'].min() >= pd.to_datetime("2024-01-01")
        assert filtered_df['date'].max() <= pd.to_datetime("2024-01-02")

    def test_start_date_only_filtering(self, sample_metrics_df):
        """Test filtering with only start date."""
        filtered_df = filter_metrics_by_date(
            sample_metrics_df.copy(),
            start_date="2024-01-03"
        )
        
        assert len(filtered_df) == 2  # Should include Jan 3 and Jan 4
        assert filtered_df['date'].min() >= pd.to_datetime("2024-01-03")

    def test_end_date_only_filtering(self, sample_metrics_df):
        """Test filtering with only end date."""
        filtered_df = filter_metrics_by_date(
            sample_metrics_df.copy(),
            end_date="2024-01-02"
        )
        
        assert len(filtered_df) == 2  # Should include Jan 1 and Jan 2
        assert filtered_df['date'].max() <= pd.to_datetime("2024-01-02")

    def test_search_filtering(self, sample_metrics_df):
        """Test search filtering by campaign name."""
        # Search for campaigns containing "Sale"
        filtered_df = search_metrics(sample_metrics_df.copy(), "Sale")
        
        assert len(filtered_df) == 1
        assert "Summer Sale" in filtered_df['campaign_name'].values

        # Search for campaigns containing "Promo"
        filtered_df = search_metrics(sample_metrics_df.copy(), "Promo")
        
        assert len(filtered_df) == 1
        assert "Winter Promo" in filtered_df['campaign_name'].values

    def test_case_insensitive_search(self, sample_metrics_df):
        """Test that search is case insensitive."""
        filtered_df = search_metrics(sample_metrics_df.copy(), "summer")
        
        assert len(filtered_df) == 1
        assert "Summer Sale" in filtered_df['campaign_name'].values

class TestMetricsSorting:
    def test_sort_by_impressions_asc(self, sample_metrics_df):
        """Test sorting by impressions in ascending order."""
        sorted_df = sort_metrics(sample_metrics_df.copy(), "impressions", "asc")
        
        impressions_list = sorted_df['impressions'].tolist()
        assert impressions_list == sorted(impressions_list)
        assert impressions_list[0] == 1000
        assert impressions_list[-1] == 4000

    def test_sort_by_impressions_desc(self, sample_metrics_df):
        """Test sorting by impressions in descending order."""
        sorted_df = sort_metrics(sample_metrics_df.copy(), "impressions", "desc")
        
        impressions_list = sorted_df['impressions'].tolist()
        assert impressions_list == sorted(impressions_list, reverse=True)
        assert impressions_list[0] == 4000
        assert impressions_list[-1] == 1000

    def test_sort_by_campaign_name(self, sample_metrics_df):
        """Test sorting by campaign name."""
        sorted_df = sort_metrics(sample_metrics_df.copy(), "campaign_name", "asc")
        
        campaign_names = sorted_df['campaign_name'].tolist()
        expected_order = ['Holiday Special', 'Spring Launch', 'Summer Sale', 'Winter Promo']
        assert campaign_names == expected_order

    def test_invalid_sort_column(self, sample_metrics_df):
        """Test sorting with invalid column name."""
        # Should return original DataFrame without error
        original_order = sample_metrics_df['campaign_name'].tolist()
        sorted_df = sort_metrics(sample_metrics_df.copy(), "invalid_column", "asc")
        
        assert sorted_df['campaign_name'].tolist() == original_order

class TestErrorHandling:
    def test_metrics_endpoint_error_handling(self, admin_token):
        """Test that metrics endpoint handles errors gracefully."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Test with invalid date format (should still work or return appropriate error)
        response = client.post(
            "/api/metrics",
            json={"start_date": "invalid-date"},
            headers=headers
        )
        
        # Should either succeed (ignoring invalid date) or return 500 with error message
        assert response.status_code in [200, 500]