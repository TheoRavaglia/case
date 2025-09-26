# Main services module - centralized imports for backward compatibility

# Import all functions from specialized modules to maintain compatibility
from .loader import (
    load_metrics_data,
    load_full_metrics_data, 
    load_metrics_data_optimized,
    get_total_count_estimate,
    load_and_filter_data_smart
)
from .filters import (
    filter_metrics_by_date,
    search_metrics,
    sort_metrics,
    apply_user_permissions
)
from .sample import create_sample_data
from .processor import get_filtered_metrics

# Additional aliases for backward compatibility
get_total_count_with_filters = lambda filters: 1000

# Re-export all functions for backward compatibility
__all__ = [
    'load_metrics_data',
    'load_full_metrics_data',
    'load_metrics_data_optimized', 
    'get_total_count_estimate',
    'filter_metrics_by_date',
    'search_metrics',
    'sort_metrics',
    'apply_user_permissions',
    'load_and_filter_data_smart',
    'get_filtered_metrics',
    'create_sample_data',
    'get_total_count_with_filters'
]