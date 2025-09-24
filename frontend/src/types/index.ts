export interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'user';
}

export interface Metric {
  date: string;
  campaign_name: string;
  impressions: number;
  clicks: number;
  cost_micros: number;
  conversions: number;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}

export interface MetricsFilter {
  startDate?: string;
  endDate?: string;
}

export type SortDirection = 'asc' | 'desc';

export interface SortConfig {
  key: keyof Metric;
  direction: SortDirection;
}