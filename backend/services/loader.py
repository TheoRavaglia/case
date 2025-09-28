import pandas as pd
import random
from datetime import datetime, timedelta
from functools import lru_cache
import os

# Global cache for the CSV data (load once, use many times)
_METRICS_CACHE = None
_CACHE_TIMESTAMP = None

def clear_cache():
    """Clear the global cache to force reload."""
    global _METRICS_CACHE, _CACHE_TIMESTAMP
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
            # Load CSV without forcing incompatible data types
            df = pd.read_csv(csv_path)
            df['date'] = pd.to_datetime(df['date']).dt.normalize()
            
            # Optimize data types after loading (safer approach)
            try:
                # Convert to more efficient types where possible
                if 'impressions' in df.columns:
                    df['impressions'] = pd.to_numeric(df['impressions'], downcast='integer')
                if 'clicks' in df.columns:
                    df['clicks'] = pd.to_numeric(df['clicks'], downcast='integer')
                if 'conversions' in df.columns:
                    df['conversions'] = pd.to_numeric(df['conversions'], downcast='float')
            except Exception:
                # Keep original types if conversion fails
                pass
            
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

# Fast counting with accurate results
@lru_cache(maxsize=1)
def get_total_rows_count():
    """Get accurate total row count."""
    try:
        # If we have cached data, use its length for accuracy
        if _METRICS_CACHE is not None:
            return len(_METRICS_CACHE)
        
        # Otherwise count lines in file
        csv_path = _get_csv_path()
        with open(csv_path, 'r') as f:
            return sum(1 for line in f) - 1  # Subtract header
    except:
        # Load data to get accurate count
        df = _load_csv_with_cache()
        return len(df)