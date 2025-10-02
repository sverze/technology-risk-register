import type { Risk, DashboardData, DropdownValues, RiskUpdate, PaginatedResponse } from '@/types/risk';
import type { RiskLogEntry, RiskLogEntryCreate, RiskLogEntryUpdate } from '@/types/riskLogEntry';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export class ApiError extends Error {
  public status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Get JWT token from localStorage
  const token = localStorage.getItem('auth_token');

  // Add Authorization header if token exists
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    headers,
    ...options,
  });

  // Handle 401 Unauthorized - redirect to login
  if (response.status === 401) {
    // Clear invalid token
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_username');

    // Redirect to login page if not already there
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }

    throw new ApiError(response.status, 'Unauthorized - please log in');
  }

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText || `HTTP ${response.status}`);
  }

  return response.json();
}

export const riskApi = {
  // Get all risks with optional filtering
  getRisks: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    category?: string;
    status?: string;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<PaginatedResponse<Risk>> => {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== '') {
          searchParams.append(key, value.toString());
        }
      });
    }
    const query = searchParams.toString() ? `?${searchParams.toString()}` : '';
    return apiRequest<PaginatedResponse<Risk>>(`/risks/${query}`);
  },

  // Get single risk by ID
  getRisk: async (riskId: string): Promise<Risk> => {
    return apiRequest<Risk>(`/risks/${riskId}`);
  },

  // Create new risk
  createRisk: async (risk: Omit<Risk, 'risk_id' | 'created_at' | 'updated_at' | 'business_disruption_net_exposure'>): Promise<Risk> => {
    return apiRequest<Risk>('/risks/', {
      method: 'POST',
      body: JSON.stringify(risk),
    });
  },

  // Update existing risk
  updateRisk: async (riskId: string, risk: Partial<Risk>): Promise<Risk> => {
    return apiRequest<Risk>(`/risks/${riskId}`, {
      method: 'PUT',
      body: JSON.stringify(risk),
    });
  },

  // Delete risk
  deleteRisk: async (riskId: string): Promise<{ message: string }> => {
    return apiRequest<{ message: string }>(`/risks/${riskId}`, {
      method: 'DELETE',
    });
  },

  // Get risk update history
  getRiskUpdates: async (riskId: string): Promise<RiskUpdate[]> => {
    return apiRequest<RiskUpdate[]>(`/risks/${riskId}/updates`);
  },

  // Get recent updates across all risks
  getRecentUpdates: async (limit?: number): Promise<RiskUpdate[]> => {
    const query = limit ? `?limit=${limit}` : '';
    return apiRequest<RiskUpdate[]>(`/risks/updates/recent${query}`);
  },
};

export const riskLogEntryApi = {
  // Create a new log entry
  createLogEntry: async (logEntry: RiskLogEntryCreate): Promise<RiskLogEntry> => {
    return apiRequest<RiskLogEntry>(`/risks/${logEntry.risk_id}/log-entries`, {
      method: 'POST',
      body: JSON.stringify(logEntry),
    });
  },

  // Get all log entries for a risk
  getLogEntries: async (riskId: string): Promise<RiskLogEntry[]> => {
    return apiRequest<RiskLogEntry[]>(`/risks/${riskId}/log-entries`);
  },

  // Get a specific log entry
  getLogEntry: async (logEntryId: string): Promise<RiskLogEntry> => {
    return apiRequest<RiskLogEntry>(`/risks/log-entries/${logEntryId}`);
  },

  // Update a log entry
  updateLogEntry: async (logEntryId: string, updates: RiskLogEntryUpdate): Promise<RiskLogEntry> => {
    return apiRequest<RiskLogEntry>(`/risks/log-entries/${logEntryId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  },

  // Approve a log entry
  approveLogEntry: async (logEntryId: string, reviewedBy: string): Promise<RiskLogEntry> => {
    return apiRequest<RiskLogEntry>(`/risks/log-entries/${logEntryId}/approve?reviewed_by=${encodeURIComponent(reviewedBy)}`, {
      method: 'POST',
    });
  },

  // Reject a log entry
  rejectLogEntry: async (logEntryId: string, reviewedBy: string): Promise<RiskLogEntry> => {
    return apiRequest<RiskLogEntry>(`/risks/log-entries/${logEntryId}/reject?reviewed_by=${encodeURIComponent(reviewedBy)}`, {
      method: 'POST',
    });
  },

  // Delete a log entry
  deleteLogEntry: async (logEntryId: string): Promise<{ message: string }> => {
    return apiRequest<{ message: string }>(`/risks/log-entries/${logEntryId}`, {
      method: 'DELETE',
    });
  },
};

export const dashboardApi = {
  // Get complete dashboard data
  getDashboard: async (): Promise<DashboardData> => {
    return apiRequest<DashboardData>('/dashboard/');
  },
};

export const dropdownApi = {
  // Get all dropdown values grouped by category
  getDropdownValues: async (): Promise<DropdownValues> => {
    // Get all dropdown values and group them by category
    const response = await apiRequest<Array<{id: number, category: string, value: string, display_order: number, is_active: boolean}>>('/dropdown/values');

    // Group by category
    const groupedResponse: Record<string, Array<{id: number, category: string, value: string, display_order: number, is_active: boolean}>> = {};
    response.forEach(item => {
      if (!groupedResponse[item.category]) {
        groupedResponse[item.category] = [];
      }
      if (item.is_active) {
        groupedResponse[item.category].push(item);
      }
    });

    // Sort each category by display_order
    Object.keys(groupedResponse).forEach(category => {
      groupedResponse[category].sort((a, b) => a.display_order - b.display_order);
    });

    // Transform the response to match our frontend DropdownValues interface
    const dropdownValues: DropdownValues = {
      categories: [],
      risk_response_strategies: [],
      departments: [],
      statuses: [],
      technology_domains: [],

      // New Business Disruption dropdowns
      business_disruption_impact_ratings: [],
      business_disruption_likelihood_ratings: [],

      // Updated control dropdowns
      controls_coverage: [],
      controls_effectiveness: [],
    };

    // Extract values from each category
    Object.entries(groupedResponse).forEach(([category, values]) => {
      const valueStrings = values.map(v => v.value);

      switch (category) {
        case 'risk_category':
        case 'category':
          dropdownValues.categories = valueStrings;
          break;
        case 'technology_domain':
          dropdownValues.technology_domains = valueStrings;
          break;
        case 'risk_response_strategy':
          dropdownValues.risk_response_strategies = valueStrings;
          break;
        case 'risk_owner_department':
        case 'department':
          dropdownValues.departments = valueStrings;
          break;
        case 'risk_status':
        case 'status':
          dropdownValues.statuses = valueStrings;
          break;
        case 'business_disruption_impact_rating':
          dropdownValues.business_disruption_impact_ratings = valueStrings;
          break;
        case 'business_disruption_likelihood_rating':
          dropdownValues.business_disruption_likelihood_ratings = valueStrings;
          break;
        case 'controls_coverage':
          dropdownValues.controls_coverage = valueStrings;
          break;
        case 'controls_effectiveness':
          dropdownValues.controls_effectiveness = valueStrings;
          break;
      }
    });

    return dropdownValues;
  },
};

export const healthApi = {
  // Health check endpoint
  getHealth: async (): Promise<{ status: string }> => {
    // Health endpoint is at root level, not under /api/v1
    const url = `${import.meta.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8008'}/health`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new ApiError(response.status, `HTTP ${response.status}`);
    }
    return response.json();
  },
};
