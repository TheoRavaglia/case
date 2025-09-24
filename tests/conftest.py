import pytest
import pandas as pd
from datetime import datetime
import sys
import os

# Add backend directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def mock_metrics_data():
    """Create small mock metrics dataset for fast testing."""
    return pd.DataFrame([
        {
            'account_id': 8181642239,
            'campaign_id': 6320590762,
            'cost_micros': 2026808000,
            'clicks': 130,
            'conversions': 6.1,
            'impressions': 4374,
            'interactions': 156,
            'date': pd.to_datetime('2024-01-15')
        },
        {
            'account_id': 8181642239,
            'campaign_id': 6862247394,
            'cost_micros': 1642249000,
            'clicks': 235,
            'conversions': 6.5,
            'impressions': 12333,
            'interactions': 282,
            'date': pd.to_datetime('2024-02-20')
        },
        {
            'account_id': 8181642239,
            'campaign_id': 3162025308,
            'cost_micros': 86707290,
            'clicks': 26,
            'conversions': 0.3,
            'impressions': 609,
            'interactions': 32,
            'date': pd.to_datetime('2024-03-10')
        },
        {
            'account_id': 8181642239,
            'campaign_id': 4957786229,
            'cost_micros': 285378200,
            'clicks': 27,
            'conversions': 0.32,
            'impressions': 529,
            'interactions': 32,
            'date': pd.to_datetime('2024-12-25')
        }
    ])

@pytest.fixture
def mock_load_metrics(monkeypatch, mock_metrics_data):
    """Mock the load_metrics_data function to return small test dataset."""
    def mock_load():
        return mock_metrics_data.copy()
    
    # Import and patch the function
    from services import load_metrics_data
    monkeypatch.setattr("services.load_metrics_data", mock_load)
    return mock_load

@pytest.fixture
def sample_metrics_df():
    """Sample metrics dataframe for testing with campaign_name column."""
    return pd.DataFrame([
        {
            'date': pd.to_datetime('2024-01-01'),
            'campaign_name': 'Summer Sale',
            'impressions': 1000,
            'clicks': 100,
            'cost_micros': 50000000,
            'conversions': 5.0,
            'conversion_rate': 0.05
        },
        {
            'date': pd.to_datetime('2024-01-02'),
            'campaign_name': 'Winter Promo', 
            'impressions': 2000,
            'clicks': 200,
            'cost_micros': 100000000,
            'conversions': 10.0,
            'conversion_rate': 0.05
        },
        {
            'date': pd.to_datetime('2024-01-03'),
            'campaign_name': 'Spring Launch',
            'impressions': 3000,
            'clicks': 300,
            'cost_micros': 150000000,
            'conversions': 15.0,
            'conversion_rate': 0.05
        },
        {
            'date': pd.to_datetime('2024-01-04'),
            'campaign_name': 'Holiday Special',
            'impressions': 4000,
            'clicks': 400,
            'cost_micros': 200000000,
            'conversions': 20.0,
            'conversion_rate': 0.05
        }
    ])

@pytest.fixture
def admin_token():
    """Get admin JWT token for testing."""
    from auth import create_access_token
    from datetime import timedelta
    
    access_token = create_access_token(
        data={"sub": "admin@company.com"}, 
        expires_delta=timedelta(minutes=15)
    )
    return access_token

@pytest.fixture
def user_token():
    """Get regular user JWT token for testing."""
    from auth import create_access_token
    from datetime import timedelta
    
    access_token = create_access_token(
        data={"sub": "user@company.com"}, 
        expires_delta=timedelta(minutes=15)
    )
    return access_token