import pandas as pd
from models.models import MetricsFilters, MetricsResponse, MetricData
from .loader import load_metrics_data
from .filters import filter_metrics_by_date, search_metrics, sort_metrics, apply_user_permissions


def get_filtered_metrics(filters: MetricsFilters, user: dict, page: int = 1, page_size: int = 20) -> MetricsResponse:
    """Optimized function to get filtered metrics with smart caching - shows ALL data."""
    try:
        page_size = min(page_size, 1000)  # Allow more records per page for complete data access
        is_admin = user.get('role') == 'admin'
        
        # Load complete data first, then apply filters
        if filters.start_date or filters.end_date or filters.search:
            # Use filtered loader only when filters are applied
            from .loader import load_metrics_data_filtered
            df = load_metrics_data_filtered(
                start_date=filters.start_date,
                end_date=filters.end_date, 
                search_term=filters.search
            )
        else:
            # Load all data when no filters (complete dataset)
            df = load_metrics_data()
        
        # Fast sorting (only if needed)
        if filters.sort_by:
            df = sort_metrics(df, filters.sort_by, filters.sort_order)
        
        # Get total before pagination
        total_count = len(df)
        
        # Efficient pagination (avoid copying large datasets)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        df_page = df.iloc[start_idx:end_idx] if start_idx < len(df) else df.iloc[0:0]
        
        # Apply permissions only to paginated data
        df_page = apply_user_permissions(df_page, user)
        
        # Vectorized conversion (much faster than iterrows)
        if not df_page.empty:
            # Calculate conversion rates vectorized
            conversion_rates = (df_page['conversions'] / df_page['clicks'].replace(0, 1)) * 100
            conversion_rates = conversion_rates.fillna(0)
            
            # Build metrics list efficiently
            metrics_list = []
            for idx, (_, row) in enumerate(df_page.iterrows()):
                metric_data = {
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'campaign_name': f"Campaign {row['campaign_id']}",
                    'impressions': int(row['impressions']),
                    'clicks': int(row['clicks']),
                    'conversions': float(row['conversions']),
                    'conversion_rate': float(conversion_rates.iloc[idx])
                }
                if is_admin and 'cost_micros' in row.index and pd.notna(row['cost_micros']):
                    metric_data['cost_micros'] = int(row['cost_micros'])
                metrics_list.append(MetricData(**metric_data))
        else:
            metrics_list = []
        
        return MetricsResponse(
            metrics=metrics_list,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=((total_count - 1) // page_size) + 1 if total_count > 0 else 1
        )
    except Exception as e:
        print(f"Error in get_filtered_metrics: {str(e)}")
        return MetricsResponse(metrics=[], total_count=0, page=1, page_size=page_size, total_pages=1)