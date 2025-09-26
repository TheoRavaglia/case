import type { LoginCredentials, LoginResponse, MetricsFilter, MetricsResponse, User } from '../types';

class ApiService {
  private baseUrl = 'https://marketing-analytics-api-nsfc.onrender.com/api';
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

  async getMetrics(filters?: MetricsFilter): Promise<MetricsResponse> {
    // Always include pagination now for better performance
    const requestData = {
      page: 1,
      page_size: 50, // Increased to 50 records per page
      ...filters
    };
    
    console.log('Sending data to API:', requestData);
    
    return this.request<MetricsResponse>('/metrics', {
      method: 'POST',
      body: JSON.stringify(requestData),
    });
  }
}

export const api = new ApiService();