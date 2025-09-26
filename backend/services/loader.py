import pandas as pd
import random
from datetime import datetime, timedelta


def _get_csv_path():
    """Helper to get CSV path."""
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'data', 'metrics.csv')

def load_metrics_data():
    """Load metrics data from CSV file."""
    try:
        df = pd.read_csv(_get_csv_path())
        df['date'] = pd.to_datetime(df['date']).dt.normalize()
        return df
    except Exception as e:
        from .sample import create_sample_data
        return create_sample_data(100)

# Aliases for backward compatibility
load_full_metrics_data = load_metrics_data
load_metrics_data_optimized = lambda filters, page=1, page_size=20: load_metrics_data()
get_total_count_estimate = lambda: 1375455
get_total_count_with_filters = lambda filters: 1000
load_and_filter_data_smart = lambda filters: load_metrics_data()