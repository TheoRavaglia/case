import pandas as pd
from datetime import datetime
from models import MetricsFilters, MetricsResponse, MetricData
from typing import List

def load_metrics_data():
    """Load metrics data from CSV file."""
    import os
    try:
        # Get the directory of this file (backend directory)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'metrics.csv')
        df = pd.read_csv(csv_path)
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        raise Exception(f"Error loading metrics data: {str(e)}")

def load_full_metrics_data():
    """Load ALL metrics data from CSV file for filtering operations."""
    import os
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'metrics.csv')
        
        print("Loading full CSV data for date filtering...")
        df = pd.read_csv(csv_path)
        
        # Convert date column to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        print(f"Loaded {len(df)} total records from CSV")
        return df
    except Exception as e:
        print(f"Error loading full metrics data: {str(e)}")
        # Fallback: return sample data
        return create_sample_data(100)

def filter_metrics_by_date(df: pd.DataFrame, start_date: str = None, end_date: str = None):
    """Filter metrics by date range."""
    try:
        initial_count = len(df)
        print(f"Date filtering - Initial records: {initial_count}")
        
        if start_date:
            start_date_parsed = pd.to_datetime(start_date)
            print(f"Filtering by start_date: {start_date_parsed}")
            df = df[df['date'] >= start_date_parsed]
            print(f"Records after start_date filter: {len(df)}")
        
        if end_date:
            end_date_parsed = pd.to_datetime(end_date)
            print(f"Filtering by end_date: {end_date_parsed}")
            df = df[df['date'] <= end_date_parsed]
            print(f"Records after end_date filter: {len(df)}")
        
        print(f"Date filtering completed: {initial_count} -> {len(df)} records")
        return df
    except Exception as e:
        print(f"Error in date filtering: {str(e)}")
        return df

def search_metrics(df: pd.DataFrame, search_term: str = None):
    """Search metrics by campaign name or ID."""
    if search_term:
        # Check which column exists and search accordingly
        if 'campaign_name' in df.columns:
            df = df[df['campaign_name'].str.contains(search_term, case=False, na=False)]
        elif 'campaign_id' in df.columns:
            # Convert campaign_id to string for search
            df = df[df['campaign_id'].astype(str).str.contains(search_term, case=False, na=False)]
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

def get_filtered_metrics(filters: MetricsFilters, user: dict, page: int = 1, page_size: int = 20) -> MetricsResponse:
    """Get metrics data with applied filters and permissions with smart pagination.
    ALWAYS uses pagination to maintain performance and usability."""
    try:
        # Maximum page_size limit to avoid overload
        page_size = min(page_size, 100)  # Maximum 100 records per page
        
        # Determine if there are active date filters
        has_date_filters = filters.start_date or filters.end_date
        
        if has_date_filters:
            # With date filters: load, filter AND paginate (never all data)
            df_filtered = load_and_filter_data_smart(filters)
            total_count = len(df_filtered)
            
            # Apply pagination even with filters
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            df = df_filtered.iloc[start_idx:end_idx]
            
            print(f"Date filter applied: {total_count} total records, showing page {page} ({len(df)} records)")
        else:
            # Without filters: direct optimized pagination
            df = load_metrics_data_optimized(filters, page, page_size)
            total_count = get_total_count_estimate()
        
        # Apply user permissions
        df = apply_user_permissions(df, user)
        
        # Convert DataFrame to list of MetricData
        metrics_list = []
        for _, row in df.iterrows():
            # Calculate conversion rate if not present
            conversion_rate = (row['conversions'] / row['clicks']) * 100 if row['clicks'] > 0 else 0
            
            metric_data = {
                'date': row['date'].strftime('%Y-%m-%d'),
                'campaign_name': f"Campaign {row['campaign_id']}",
                'impressions': int(float(row['impressions'])),
                'clicks': int(float(row['clicks'])),
                'conversions': float(row['conversions']),
                'conversion_rate': float(conversion_rate)
            }
            
            # Include cost_micros only if user is admin and column exists
            if user.get('role') == 'admin' and 'cost_micros' in row.index:
                metric_data['cost_micros'] = int(row['cost_micros']) if pd.notna(row['cost_micros']) else None
            
            metrics_list.append(MetricData(**metric_data))
        
        return MetricsResponse(
            metrics=metrics_list,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=((total_count - 1) // page_size) + 1 if total_count > 0 else 1
        )
    except Exception as e:
        print(f"Error in get_filtered_metrics: {str(e)}")
        # Return empty response in case of error
        return MetricsResponse(
            metrics=[],
            total_count=0
        )

def load_metrics_data_optimized(filters: MetricsFilters, page: int = 1, page_size: int = 20):
    """Load metrics data with super optimization for large datasets."""
    import os
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'metrics.csv')
        
        print(f"Loading page {page} with {page_size} records...")
        
        # Para arquivos muito grandes, vamos usar uma abordagem mais rápida
        # Lemos apenas as primeiras linhas necessárias + paginação
        skip_rows = (page - 1) * page_size + 1  # +1 para pular header na primeira iteração
        
        # Estratégia super rápida: ler diretamente as linhas que precisamos
        try:
            # Para a primeira página, lemos direto do início
            if page == 1:
                df = pd.read_csv(csv_path, nrows=page_size)
            else:
                # Para outras páginas, pulamos as linhas anteriores
                df = pd.read_csv(csv_path, skiprows=skip_rows, nrows=page_size, header=None)
                # Adiciona o header manualmente
                header_df = pd.read_csv(csv_path, nrows=0)
                df.columns = header_df.columns
            
            print(f"Loaded {len(df)} records successfully")
            
            # Convert date column to datetime if it exists
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            
            return df
            
        except Exception as load_error:
            print(f"Fast load failed: {load_error}, using fallback...")
            # Fallback: dados de exemplo
            return create_sample_data(page_size)
            
    except Exception as e:
        print(f"Error loading metrics data: {str(e)}")
        return create_sample_data(page_size)

def create_sample_data(page_size: int = 20):
    """Create sample data when CSV loading fails."""
    import random
    from datetime import datetime, timedelta
    
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

def load_and_filter_data_smart(filters: MetricsFilters):
    """Load and filter data with smart optimization for large datasets."""
    try:
        # Load complete CSV only when necessary
        df = load_full_metrics_data()
        
        # Apply date filters
        if filters.start_date or filters.end_date:
            df = filter_metrics_by_date(df, filters.start_date, filters.end_date)
        
        # Apply search if specified
        if filters.search:
            df = search_metrics(df, filters.search)
        
        # Apply sorting
        df = sort_metrics(df, filters.sort_by, filters.sort_order)
        
        # IMPORTANT: Limit maximum result to avoid overload
        MAX_FILTERED_RESULTS = 1000
        if len(df) > MAX_FILTERED_RESULTS:
            print(f"Warning: Filtering returned {len(df)} records, limiting to {MAX_FILTERED_RESULTS} for performance")
            df = df.head(MAX_FILTERED_RESULTS)
        
        return df
    except Exception as e:
        print(f"Error in smart filtering: {str(e)}")
        return create_sample_data(20)

def get_total_count_estimate() -> int:
    """Get estimated total count without loading full dataset."""
    import os
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, 'metrics.csv')
        
        # Count lines optimized way
        with open(csv_path, 'r') as f:
            count = sum(1 for _ in f) - 1  # -1 for header
        return count
    except Exception:
        return 1000000  # Default estimate

def get_total_count_with_filters(filters: MetricsFilters) -> int:
    """Get total count of records matching filters (fast estimation)."""
    # For demonstration, we return a fixed estimate
    # In production, this would be calculated via database or cache
    return 1000  # Quick estimate to avoid counting 1M+ lines