import React, { useState, useEffect } from 'react'
import { api } from '../services/api'

function MetricsTable({ user }) {
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({
    start_date: '',
    end_date: '',
    search: '',
    sort_by: '',
    sort_order: 'asc'
  })
  const [totalCount, setTotalCount] = useState(0)

  const loadMetrics = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await api.getMetrics(filters)
      setMetrics(response.metrics)
      setTotalCount(response.total_count)
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to load metrics')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMetrics()
  }, [filters])

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilters(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSort = (column) => {
    setFilters(prev => ({
      ...prev,
      sort_by: column,
      sort_order: prev.sort_by === column && prev.sort_order === 'asc' ? 'desc' : 'asc'
    }))
  }

  const clearFilters = () => {
    setFilters({
      start_date: '',
      end_date: '',
      search: '',
      sort_by: '',
      sort_order: 'asc'
    })
  }

  const formatCurrency = (micros) => {
    if (micros === null || micros === undefined) return 'N/A'
    return `$${(micros / 1000000).toFixed(2)}`
  }

  const getSortIcon = (column) => {
    if (filters.sort_by !== column) return ' ↕️'
    return filters.sort_order === 'asc' ? ' ↑' : ' ↓'
  }

  return (
    <div className="card">
      <h2>Marketing Metrics Dashboard</h2>
      <p>Showing {totalCount} records</p>
      
      {error && <div className="error">{error}</div>}
      
      <div className="filters">
        <div className="form-group">
          <label htmlFor="start_date">Start Date:</label>
          <input
            type="date"
            id="start_date"
            name="start_date"
            value={filters.start_date}
            onChange={handleFilterChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="end_date">End Date:</label>
          <input
            type="date"
            id="end_date"
            name="end_date"
            value={filters.end_date}
            onChange={handleFilterChange}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="search">Search Campaign:</label>
          <input
            type="text"
            id="search"
            name="search"
            value={filters.search}
            onChange={handleFilterChange}
            placeholder="Search by campaign name"
          />
        </div>
        
        <div className="form-group">
          <label>&nbsp;</label>
          <button className="btn" onClick={clearFilters}>
            Clear Filters
          </button>
        </div>
      </div>
      
      {loading ? (
        <div className="loading">Loading metrics...</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th onClick={() => handleSort('date')}>
                  Date{getSortIcon('date')}
                </th>
                <th onClick={() => handleSort('campaign_name')}>
                  Campaign Name{getSortIcon('campaign_name')}
                </th>
                <th onClick={() => handleSort('impressions')}>
                  Impressions{getSortIcon('impressions')}
                </th>
                <th onClick={() => handleSort('clicks')}>
                  Clicks{getSortIcon('clicks')}
                </th>
                {user.role === 'admin' && (
                  <th onClick={() => handleSort('cost_micros')}>
                    Cost{getSortIcon('cost_micros')}
                  </th>
                )}
                <th onClick={() => handleSort('conversions')}>
                  Conversions{getSortIcon('conversions')}
                </th>
                <th onClick={() => handleSort('conversion_rate')}>
                  Conversion Rate{getSortIcon('conversion_rate')}
                </th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((metric, index) => (
                <tr key={index}>
                  <td>{metric.date}</td>
                  <td>{metric.campaign_name}</td>
                  <td>{metric.impressions.toLocaleString()}</td>
                  <td>{metric.clicks.toLocaleString()}</td>
                  {user.role === 'admin' && (
                    <td>{formatCurrency(metric.cost_micros)}</td>
                  )}
                  <td>{metric.conversions}</td>
                  <td>{(metric.conversion_rate * 100).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {metrics.length === 0 && (
            <div className="loading">No metrics found matching your criteria</div>
          )}
        </div>
      )}
    </div>
  )
}

export default MetricsTable