import { useState, useEffect } from 'react';
import type { Metric, User, MetricsFilter, SortConfig, SortDirection } from '../types';
import { api } from '../services/api';

interface MetricsTableProps {
  user: User;
}

export default function MetricsTable({ user }: MetricsTableProps) {
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState<MetricsFilter>({ page: 1, page_size: 50 });
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'date', direction: 'desc' });
  const [pagination, setPagination] = useState({
    total_count: 0,
    page: 1,
    page_size: 50,
    total_pages: 1
  });

  useEffect(() => {
    // Load initial data only on first render
    loadMetrics();
  }, []); // Remove dependency on filters to avoid automatic reloads

  // Function to check if there are active filters
  const hasActiveFilters = () => {
    return !!(filters.start_date || filters.end_date);
  };

  // Function to clear all filters
  const clearAllFilters = () => {
    setFilters({ page: 1, page_size: 50 }); // Reset filters, pagination, and column filters
    setSortConfig({ key: 'date', direction: 'desc' });
    loadMetricsWithFilters({ page: 1, page_size: 50 });
  };

  const applyFilters = () => loadMetricsWithFilters(filters);

  const loadMetricsWithFilters = async (filterParams: MetricsFilter) => {
    setLoading(true);
    setError('');
    try {
      const response = await api.getMetrics(filterParams);
      setMetrics(response.metrics);
      setPagination(response);
    } catch (err) {
      setError('Error loading metrics');
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = () => loadMetricsWithFilters(filters);

  const goToPage = (page: number) => {
    const newFilters = { ...filters, page };
    setFilters(newFilters);
    loadMetricsWithFilters(newFilters);
  };

  const handleSort = (key: keyof Metric) => {
    let direction: SortDirection = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
    
    // Send sorting to backend and reload data
    const newFilters = {
      ...filters,
      sort_by: key,
      sort_order: direction
    };
    setFilters(newFilters);
    loadMetricsWithFilters(newFilters);
  };



  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value / 1000000); // cost_micros to reais
  };

  const formatDate = (dateStr: string) => {
    // Backend returns YYYY-MM-DD format - simple display conversion
    return dateStr.split('-').reverse().join('/'); // YYYY-MM-DD -> DD/MM/YYYY
  };

  const getSortIcon = (columnKey: keyof Metric) => {
    if (sortConfig.key !== columnKey) return '↕️';
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="metrics-container">
      <h2>Metrics Dashboard</h2>
      
      {/* Date Filters */}
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="startDate">Start Date:</label>
          <input
            type="date"
            id="startDate"
            value={filters.start_date || ''}
            onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            placeholder="Select start date"
          />
        </div>
        <div className="filter-group">
          <label htmlFor="endDate">End Date:</label>
          <input
            type="date"
            id="endDate"
            value={filters.end_date || ''}
            onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            placeholder="Select end date"
          />
        </div>
        <div className="filter-actions">
          <button 
            onClick={clearAllFilters} 
            className="btn btn-clear"
            disabled={!hasActiveFilters()}
            title="Remove all applied filters"
          >
            🗑️ Clear Filters
          </button>
          <button 
            onClick={applyFilters} 
            className="btn btn-apply"
            disabled={loading}
            title="Apply selected date filters"
          >
            {loading ? '⏳ Loading...' : '🔍 Apply Date Filter'}
          </button>
        </div>
        
        {/* Filter feedback */}
        {hasActiveFilters() && (
          <div className="filter-feedback">
            <div className="filter-info">
              <span className="filter-icon">📅</span>
              <strong>Active filters:</strong>
              {filters.start_date && (
                <span className="filter-tag">
                  From: {new Date(filters.start_date + 'T00:00:00').toLocaleDateString('en-GB')}
                </span>
              )}
              {filters.end_date && (
                <span className="filter-tag">
                  To: {new Date(filters.end_date + 'T00:00:00').toLocaleDateString('en-GB')}
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="table-container" style={{ minHeight: '500px', display: 'flex', flexDirection: 'column' }}>
        {loading ? (
          <div className="loading" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p>🔄 Loading metrics...</p>
          </div>
        ) : metrics.length === 0 ? (
          <div className="no-data">
            <p>📊 No data found for the selected criteria.</p>
            {hasActiveFilters() && (
              <p>Try adjusting your date range or clearing filters to see more results.</p>
            )}
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th onClick={() => handleSort('date')}>
                  Date {getSortIcon('date')}
                </th>
                <th onClick={() => handleSort('campaign_id')}>
                  Campaign {getSortIcon('campaign_id')}
                </th>
                <th onClick={() => handleSort('impressions')}>
                  Impressions {getSortIcon('impressions')}
                </th>
                <th onClick={() => handleSort('clicks')}>
                  Clicks {getSortIcon('clicks')}
                </th>
                <th onClick={() => handleSort('conversions')}>
                  Conversions {getSortIcon('conversions')}
                </th>
                {/* Backend handles cost_micros permission - only shows if user is admin */}
                {metrics.length > 0 && metrics[0].cost_micros !== undefined && (
                  <th onClick={() => handleSort('cost_micros')}>
                    Cost {getSortIcon('cost_micros')}
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric, index) => (
                <tr key={index}>
                  <td>{formatDate(metric.date)}</td>
                  <td>{metric.campaign_name}</td>
                  <td>{metric.impressions.toLocaleString()}</td>
                  <td>{metric.clicks.toLocaleString()}</td>
                  <td>{metric.conversions.toLocaleString()}</td>
                  {/* Backend controls cost_micros visibility */}
                  {metric.cost_micros !== undefined && (
                    <td>{formatCurrency(metric.cost_micros)}</td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {!loading && (
        <div className="pagination-container">
          <div className="pagination-info">
            <p>
              Showing {((pagination.page - 1) * pagination.page_size) + 1} to {Math.min(pagination.page * pagination.page_size, pagination.total_count)} of {pagination.total_count.toLocaleString()} records
            </p>
            <p>Page {pagination.page} of {pagination.total_pages}</p>
          </div>
        
        <div className="pagination-controls">
          <button 
            onClick={() => pagination.page > 1 && goToPage(pagination.page - 1)} 
            disabled={pagination.page <= 1}
            className="btn btn-secondary"
          >
            ← Previous
          </button>
          
          <span className="page-numbers">
            {Array.from({ length: Math.min(5, pagination.total_pages) }, (_, i) => {
              const pageNum = Math.max(1, Math.min(pagination.total_pages - 4, pagination.page - 2)) + i;
              if (pageNum <= pagination.total_pages) {
                return (
                  <button
                    key={pageNum}
                    onClick={() => goToPage(pageNum)}
                    className={`btn ${pagination.page === pageNum ? 'btn-primary' : 'btn-secondary'}`}
                  >
                    {pageNum}
                  </button>
                );
              }
              return null;
            })}
          </span>
          
          <button 
            onClick={() => pagination.page < pagination.total_pages && goToPage(pagination.page + 1)} 
            disabled={pagination.page >= pagination.total_pages}
            className="btn btn-secondary"
          >
            Next →
          </button>
        </div>
        </div>
      )}

      {!loading && (
        <div className="metrics-summary">
          <p>Total: {pagination.total_count.toLocaleString()} records | {user.role === 'admin' ? '✅ Admin access' : 'ℹ️ Regular user'}</p>
        </div>
      )}
    </div>
  );
}