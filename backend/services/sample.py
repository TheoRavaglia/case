import pandas as pd
import random
from datetime import datetime, timedelta


def create_sample_data(page_size: int = 20):
    """Create sample data when CSV loading fails."""
    data = []
    base_date = datetime(2024, 8, 1)
    for i in range(page_size):
        data.append({
            'date': base_date + timedelta(days=i),
            'campaign_id': 6320590000 + i,
            'impressions': random.randint(10000, 50000),
            'clicks': random.randint(500, 2000), 
            'conversions': round(random.uniform(20, 100), 2),
            'cost_micros': random.randint(1000000, 5000000),
            'account_id': 8181642239,
            'interactions': random.randint(600, 2500)
        })
    return pd.DataFrame(data)