import type { LoginCredentials, LoginResponse, Metric, MetricsFilter, User } from '../types';

class ApiService {
  private baseUrl = 'http://localhost:8080/api';
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
      signal: AbortSignal.timeout(30000), // 30 second timeout
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    return this.request<LoginResponse>('/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/me');
  }

  async getMetrics(filters?: MetricsFilter): Promise<{ metrics: Metric[]; total_count: number }> {
    // Adiciona configurações padrão para otimização
    const defaultFilters = {
      page: 1,
      page_size: 20,
      ...filters
    };
    
    return this.request<{ metrics: Metric[]; total_count: number }>('/metrics', {
      method: 'POST',
      body: JSON.stringify(defaultFilters),
    });
  }
}

export const api = new ApiService();