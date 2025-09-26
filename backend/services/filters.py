import pandas as pd


def filter_metrics_by_date(df: pd.DataFrame, start_date: str = None, end_date: str = None):
    """Filter metrics by date range."""
    if start_date:
        start_parsed = pd.to_datetime(start_date).normalize()
        df = df[df['date'].dt.normalize() >= start_parsed]
    if end_date:
        end_parsed = pd.to_datetime(end_date).normalize()
        df = df[df['date'].dt.normalize() <= end_parsed]
    return df

def search_metrics(df: pd.DataFrame, search_term: str = None):
    """Search metrics by campaign name or ID."""
    if search_term:
        if 'campaign_name' in df.columns:
            df = df[df['campaign_name'].str.contains(search_term, case=False, na=False)]
        elif 'campaign_id' in df.columns:
            df = df[df['campaign_id'].astype(str).str.contains(search_term, case=False, na=False)]
    return df

def sort_metrics(df: pd.DataFrame, sort_by: str = None, sort_order: str = "asc"):
    """Sort metrics by specified column."""
    if sort_by and sort_by in df.columns:
        ascending = sort_order.lower() == "asc"
        if sort_by == 'date':
            df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.normalize()
        df = df.sort_values(by=sort_by, ascending=ascending)
    return df

def apply_user_permissions(df: pd.DataFrame, user: dict):
    """Apply user role-based permissions to data."""
    if user.get('role') != 'admin' and 'cost_micros' in df.columns:
        df = df.drop('cost_micros', axis=1)
    return df