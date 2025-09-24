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

  const loadMetrics = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.getMetrics(filters);
      setMetrics(response.metrics);
    } catch (err) {
      setError('Erro ao carregar métricas');
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (key: keyof Metric) => {
    let direction: SortDirection = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
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
        <div>
          <label htmlFor="startDate">Data Inicial:</label>
          <input
            type="date"
            id="startDate"
            value={filters.startDate || ''}
            onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
          />
        </div>
        <div>
          <label htmlFor="endDate">Data Final:</label>
          <input
            type="date"
            id="endDate"
            value={filters.endDate || ''}
            onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
          />
        </div>
        <button onClick={() => setFilters({})}>Limpar Filtros</button>
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