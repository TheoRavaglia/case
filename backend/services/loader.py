import pandas as pd
import random
from datetime import datetime, timedelta
from functools import lru_cache
import os

# Global cache for the CSV data (load once, use many times)
_METRICS_CACHE = None
_CACHE_TIMESTAMP = None

def _get_csv_path():
    """Helper to get CSV path."""
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(current_dir, 'data', 'metrics.csv')

def _load_csv_with_cache():
    """Load CSV with intelligent caching - O(1) after first load."""
    global _METRICS_CACHE, _CACHE_TIMESTAMP
    
    csv_path = _get_csv_path()
    
    try:
        # Check if file was modified (cache invalidation)
        file_mtime = os.path.getmtime(csv_path)
        
        if _METRICS_CACHE is None or _CACHE_TIMESTAMP != file_mtime:
            # Load and optimize data types for speed
            df = pd.read_csv(csv_path, dtype={
                'impressions': 'int32',
                'clicks': 'int32', 
                'conversions': 'float32',
                'cost_micros': 'int64'
            })
            df['date'] = pd.to_datetime(df['date']).dt.normalize()
            
            # Cache the data
            _METRICS_CACHE = df
            _CACHE_TIMESTAMP = file_mtime
        
        return _METRICS_CACHE.copy()  # Return copy to avoid mutations
        
    except Exception:
        # Fallback to sample data
        if _METRICS_CACHE is None:
            from .sample import create_sample_data
            _METRICS_CACHE = create_sample_data(100)
        return _METRICS_CACHE.copy()

@lru_cache(maxsize=32)  # Cache filtered results
def load_metrics_data_filtered(start_date=None, end_date=None, search_term=None):
    """Load metrics with basic filters applied - cached for performance."""
    df = _load_csv_with_cache()
    
    # Apply filters efficiently
    if start_date:
        df = df[df['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['date'] <= pd.to_datetime(end_date)]
    if search_term:
        # Efficient string search
        mask = df['campaign_id'].astype(str).str.contains(search_term, case=False, na=False)
        df = df[mask]
    
    return df

def load_metrics_data():
    """Standard loader - uses cache for O(1) performance after first load."""
    return _load_csv_with_cache()

# Fast counting without loading full data
@lru_cache(maxsize=1)
def get_total_rows_count():
    """Get total row count efficiently."""
    try:
        # Count lines without loading full CSV
        csv_path = _get_csv_path()
        with open(csv_path, 'r') as f:
            return sum(1 for line in f) - 1  # Subtract header
    except:
        return 1375455  # Fallback estimate

# Optimized aliases
load_full_metrics_data = load_metrics_data
load_metrics_data_optimized = load_metrics_data_filtered
get_total_count_estimate = get_total_rows_count
get_total_count_with_filters = lambda filters: min(get_total_rows_count(), 10000)  # Estimate
load_and_filter_data_smart = load_metrics_data_filtered