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
  const [filters, setFilters] = useState<MetricsFilter>({});
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'date', direction: 'desc' });

  useEffect(() => {
    loadMetrics();
  }, [filters]);

  // Função para verificar se há filtros ativos
  const hasActiveFilters = () => {
    return !!(filters.start_date || filters.end_date);
  };

  // Função para limpar todos os filtros
  const clearAllFilters = () => {
    setFilters({});
    setSortConfig({ key: 'date', direction: 'desc' });
    // Recarrega dados sem filtros
    loadMetricsWithFilters({});
  };

  // Função para aplicar filtros
  const applyFilters = () => {
    loadMetricsWithFilters(filters);
  };

  // Função auxiliar para carregar métricas com filtros específicos
  const loadMetricsWithFilters = async (filterParams: MetricsFilter) => {
    setLoading(true);
    setError('');
    try {
      const response = await api.getMetrics(filterParams);
      setMetrics(response.metrics);
    } catch (err) {
      setError('Erro ao carregar métricas');
      console.error('Erro:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    loadMetricsWithFilters(filters);
  };

  const handleSort = (key: keyof Metric) => {
    let direction: SortDirection = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
    
    // Enviar ordenação para o backend também
    setFilters({
      ...filters,
      sort_by: key,
      sort_order: direction
    });
  };

  const sortedMetrics = [...metrics].sort((a, b) => {
    const aVal = a[sortConfig.key];
    const bVal = b[sortConfig.key];
    
    if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value / 1000000); // cost_micros para reais
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR');
  };

  const getSortIcon = (columnKey: keyof Metric) => {
    if (sortConfig.key !== columnKey) return '↕️';
    return sortConfig.direction === 'asc' ? '↑' : '↓';
  };

  if (loading) {
    return <div className="loading">Carregando métricas...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="metrics-container">
      <h2>Dashboard de Métricas</h2>
      
      {/* Filtros por Data */}
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="startDate">Data Inicial:</label>
          <input
            type="date"
            id="startDate"
            value={filters.start_date || ''}
            onChange={(e) => setFilters({ ...filters, start_date: e.target.value })}
            max="2024-12-31"
            min="2024-01-01"
          />
        </div>
        <div className="filter-group">
          <label htmlFor="endDate">Data Final:</label>
          <input
            type="date"
            id="endDate"
            value={filters.end_date || ''}
            onChange={(e) => setFilters({ ...filters, end_date: e.target.value })}
            max="2024-12-31"
            min="2024-01-01"
          />
        </div>
        <div className="filter-actions">
          <button 
            onClick={clearAllFilters} 
            className="btn btn-clear"
            disabled={!hasActiveFilters()}
            title="Remove todos os filtros aplicados"
          >
            🗑️ Limpar Filtros
          </button>
          <button 
            onClick={applyFilters} 
            className="btn btn-apply"
            disabled={loading}
            title="Aplica os filtros de data selecionados"
          >
            {loading ? '⏳ Carregando...' : '🔍 Aplicar Filtros'}
          </button>
        </div>
        
        {/* Feedback dos filtros */}
        {hasActiveFilters() && (
          <div className="filter-feedback">
            <div className="filter-info">
              <span className="filter-icon">📅</span>
              <strong>Filtros ativos:</strong>
              {filters.start_date && (
                <span className="filter-tag">
                  De: {new Date(filters.start_date).toLocaleDateString('pt-BR')}
                </span>
              )}
              {filters.end_date && (
                <span className="filter-tag">
                  Até: {new Date(filters.end_date).toLocaleDateString('pt-BR')}
                </span>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Tabela */}
      <div className="table-container">
        <table className="table">
          <thead>
            <tr>
              <th onClick={() => handleSort('date')}>
                Data {getSortIcon('date')}
              </th>
              <th onClick={() => handleSort('campaign_name')}>
                Campanha {getSortIcon('campaign_name')}
              </th>
              <th onClick={() => handleSort('impressions')}>
                Impressões {getSortIcon('impressions')}
              </th>
              <th onClick={() => handleSort('clicks')}>
                Cliques {getSortIcon('clicks')}
              </th>
              <th onClick={() => handleSort('conversions')}>
                Conversões {getSortIcon('conversions')}
              </th>
              {/* Coluna cost_micros só para admin */}
              {user.role === 'admin' && (
                <th onClick={() => handleSort('cost_micros')}>
                  Custo {getSortIcon('cost_micros')}
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
      </div>

      <div className="metrics-summary">
        <p>Total de registros: {metrics.length}</p>
        {user.role === 'admin' && <p>✅ Dados financeiros visíveis (Admin)</p>}
        {user.role !== 'admin' && <p>ℹ️ Dados financeiros ocultos (Usuário comum)</p>}
      </div>
    </div>
  );
}