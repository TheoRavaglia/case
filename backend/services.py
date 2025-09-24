import pandas as pd
from datetime import datetime
from models import MetricsFilters, MetricsResponse, MetricData
from typing import List

def load_metrics_data():
    """Load metrics data from CSV file."""
    try:
        df = pd.read_csv('metrics.csv')
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        raise Exception(f"Error loading metrics data: {str(e)}")

def filter_metrics_by_date(df: pd.DataFrame, start_date: str = None, end_date: str = None):
    """Filter metrics by date range."""
    if start_date:
        start_date = pd.to_datetime(start_date)
        df = df[df['date'] >= start_date]
    
    if end_date:
        end_date = pd.to_datetime(end_date)
        df = df[df['date'] <= end_date]
    
    return df

def search_metrics(df: pd.DataFrame, search_term: str = None):
    """Search metrics by campaign name."""
    if search_term:
        df = df[df['campaign_name'].str.contains(search_term, case=False, na=False)]
    return df

def sort_metrics(df: pd.DataFrame, sort_by: str = None, sort_order: str = "asc"):
    """Sort metrics by specified column."""
    if sort_by and sort_by in df.columns:
        ascending = sort_order.lower() == "asc"
        df = df.sort_values(by=sort_by, ascending=ascending)
    return df

def apply_user_permissions(df: pd.DataFrame, user: dict):
    """Apply user role-based permissions to data."""
    # Hide cost_micros column for non-admin users
    if user.get('role') != 'admin' and 'cost_micros' in df.columns:
        df = df.drop('cost_micros', axis=1)
    return df

def get_filtered_metrics(filters: MetricsFilters, user: dict) -> MetricsResponse:
    """Get metrics data with applied filters and permissions."""
    # Load data
    df = load_metrics_data()
    
    # Apply filters
    if filters.start_date or filters.end_date:
        df = filter_metrics_by_date(df, filters.start_date, filters.end_date)
    
    if filters.search:
        df = search_metrics(df, filters.search)
    
    if filters.sort_by:
        df = sort_metrics(df, filters.sort_by, filters.sort_order)
    
    # Apply user permissions
    df = apply_user_permissions(df, user)
    
    # Convert to response format
    total_count = len(df)
    
    # Convert DataFrame to list of MetricData
    metrics_list = []
    for _, row in df.iterrows():
        metric_data = {
            'date': row['date'].strftime('%Y-%m-%d'),
            'campaign_name': row['campaign_name'],
            'impressions': int(row['impressions']),
            'clicks': int(row['clicks']),
            'conversions': float(row['conversions']),
            'conversion_rate': float(row['conversion_rate'])
        }
        
        # Include cost_micros only if user is admin and column exists
        if user.get('role') == 'admin' and 'cost_micros' in row.index:
            metric_data['cost_micros'] = int(row['cost_micros']) if pd.notna(row['cost_micros']) else None
        
        metrics_list.append(MetricData(**metric_data))
    
    return MetricsResponse(
        metrics=metrics_list,
        total_count=total_count
    )