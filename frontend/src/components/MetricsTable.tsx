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
    setFilters({});
    setSortConfig({ key: 'date', direction: 'desc' });
    // Reload data without filters
    loadMetricsWithFilters({});
  };

  // Function to apply filters
  const applyFilters = () => {
    console.log('Applying filters:', filters);
    console.log('Are there date filters?', hasActiveFilters());
    loadMetricsWithFilters(filters);
  };

  // Helper function to load metrics with specific filters
  const loadMetricsWithFilters = async (filterParams: MetricsFilter) => {
    setLoading(true);
    setError('');
    try {
      console.log('Sending filters to API:', filterParams);
      const response = await api.getMetrics(filterParams);
      console.log('API response:', response);
      
      setMetrics(response.metrics);
      setPagination({
        total_count: response.total_count,
        page: response.page,
        page_size: response.page_size,
        total_pages: response.total_pages
      });
    } catch (err) {
      setError('Error loading metrics');
      console.error('Error loading metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    loadMetricsWithFilters(filters);
  };

  // Pagination functions
  const goToPage = (page: number) => {
    const newFilters = { ...filters, page };
    setFilters(newFilters);
    loadMetricsWithFilters(newFilters);
  };

  const goToPreviousPage = () => {
    if (pagination.page > 1) {
      goToPage(pagination.page - 1);
    }
  };

  const goToNextPage = () => {
    if (pagination.page < pagination.total_pages) {
      goToPage(pagination.page + 1);
    }
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

  const sortedMetrics = [...metrics].sort((a, b) => {
    let aVal = a[sortConfig.key];
    let bVal = b[sortConfig.key];
    
    // Special handling for date sorting
    if (sortConfig.key === 'date') {
      aVal = new Date(aVal as string).getTime();
      bVal = new Date(bVal as string).getTime();
    }
    
    if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value / 1000000); // cost_micros to reais
  };

  const formatDate = (dateStr: string) => {
    // Ensure consistent date formatting without timezone issues
    const date = new Date(dateStr + 'T00:00:00');
    return date.toLocaleDateString('en-GB');
  };

  const getSortIcon = (columnKey: keyof Metric) => {
    if (sortConfig.key !== columnKey) return '↕️';
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  if (loading) {
    return <div className="loading">Loading metrics...</div>;
  }

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
            onChange={(e) => {
              console.log('Start date changed:', e.target.value);
              setFilters({ ...filters, start_date: e.target.value });
            }}
            placeholder="Select start date"
          />
        </div>
        <div className="filter-group">
          <label htmlFor="endDate">End Date:</label>
          <input
            type="date"
            id="endDate"
            value={filters.end_date || ''}
            onChange={(e) => {
              console.log('End date changed:', e.target.value);
              setFilters({ ...filters, end_date: e.target.value });
            }}
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
            {loading ? '⏳ Loading...' : '🔍 Apply Filters'}
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
      <div className="table-container">
        {sortedMetrics.length === 0 ? (
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
                <th onClick={() => handleSort('campaign_name')}>
                  Campaign {getSortIcon('campaign_name')}
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
                {/* cost_micros column only for admin */}
                {user.role === 'admin' && (
                  <th onClick={() => handleSort('cost_micros')}>
                    Cost {getSortIcon('cost_micros')}
                  </th>
                )}
              </tr>
            </thead>
            <tbody>
              {sortedMetrics.map((metric, index) => (
                <tr key={index}>
                  <td>{formatDate(metric.date)}</td>
                  <td>{metric.campaign_name}</td>
                  <td>{metric.impressions.toLocaleString()}</td>
                  <td>{metric.clicks.toLocaleString()}</td>
                  <td>{metric.conversions.toLocaleString()}</td>
                  {user.role === 'admin' && (
                    <td>{formatCurrency(metric.cost_micros)}</td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      <div className="pagination-container">
        <div className="pagination-info">
          <p>
            Showing {((pagination.page - 1) * pagination.page_size) + 1} to {Math.min(pagination.page * pagination.page_size, pagination.total_count)} of {pagination.total_count.toLocaleString()} records
          </p>
          <p>Page {pagination.page} of {pagination.total_pages}</p>
        </div>
        
        <div className="pagination-controls">
          <button 
            onClick={goToPreviousPage} 
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
            onClick={goToNextPage} 
            disabled={pagination.page >= pagination.total_pages}
            className="btn btn-secondary"
          >
            Next →
          </button>
        </div>
      </div>

      <div className="metrics-summary">
        <p>Total records: {pagination.total_count.toLocaleString()}</p>
        {user.role === 'admin' && <p>✅ Financial data visible (Admin)</p>}
        {user.role !== 'admin' && <p>ℹ️ Financial data hidden (Regular user)</p>}
      </div>
    </div>
  );
}