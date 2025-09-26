import pandas as pd
from models.models import MetricsFilters, MetricsResponse, MetricData
from .loader import load_metrics_data
from .filters import filter_metrics_by_date, search_metrics, sort_metrics, apply_user_permissions


def get_filtered_metrics(filters: MetricsFilters, user: dict, page: int = 1, page_size: int = 20) -> MetricsResponse:
    """Main function to get filtered metrics with pagination."""
    try:
        page_size = min(page_size, 100)  # Max 100 per page
        
        # Load and filter data
        df = load_metrics_data()
        if filters.start_date or filters.end_date:
            df = filter_metrics_by_date(df, filters.start_date, filters.end_date)
        if filters.search:
            df = search_metrics(df, filters.search)
        df = sort_metrics(df, filters.sort_by, filters.sort_order)
        
        # Apply pagination
        total_count = len(df)
        start_idx = (page - 1) * page_size
        df = df.iloc[start_idx:start_idx + page_size]
        
        # Apply permissions
        df = apply_user_permissions(df, user)
        is_admin = user.get('role') == 'admin'
        
        # Convert to response format
        metrics_list = []
        for _, row in df.iterrows():
            conversion_rate = (row['conversions'] / row['clicks']) * 100 if row['clicks'] > 0 else 0
            metric_data = {
                'date': row['date'].strftime('%Y-%m-%d'),
                'campaign_name': f"Campaign {row['campaign_id']}",
                'impressions': int(float(row['impressions'])),
                'clicks': int(float(row['clicks'])),
                'conversions': float(row['conversions']),
                'conversion_rate': float(conversion_rate)
            }
            if is_admin and 'cost_micros' in row.index and pd.notna(row['cost_micros']):
                metric_data['cost_micros'] = int(row['cost_micros'])
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
        return MetricsResponse(metrics=[], total_count=0)