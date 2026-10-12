// Centralized API client for SpendSense AI
// Prioritizes VITE_API_BASE_URL, with backward compatibility for VITE_API_URL
let rawBaseUrl = (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || '').trim();
// If host is passed without protocol (e.g. from Render fromService property: host), prepend https://
if (rawBaseUrl && !rawBaseUrl.startsWith('http://') && !rawBaseUrl.startsWith('https://')) {
  rawBaseUrl = `https://${rawBaseUrl}`;
}
// Strip trailing slash; in local development default to http://127.0.0.1:8000, in production default to same-origin relative URL
const API_BASE_URL = rawBaseUrl ? rawBaseUrl.replace(/\/+$/, '') : (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '');

function getAuthHeaders() {
  const token = localStorage.getItem('spendsense_token');
  const headers = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const headers = {
    ...getAuthHeaders(),
    ...(options.headers || {}),
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401 && localStorage.getItem('spendsense_token')) {
    // Token may have expired
    localStorage.removeItem('spendsense_token');
    localStorage.removeItem('spendsense_user');
    window.dispatchEvent(new Event('auth-changed'));
  }

  if (!response.ok) {
    let errorDetail = `Request failed (${response.status})`;
    try {
      const errorJson = await response.json();
      if (typeof errorJson.detail === 'string') {
        errorDetail = errorJson.detail;
      } else if (Array.isArray(errorJson.detail)) {
        errorDetail = errorJson.detail.map((d) => d.msg || d).join(', ');
      }
    } catch {
      const text = await response.text();
      if (text) errorDetail = text;
    }
    throw new Error(errorDetail);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  // System Health
  async getStatus() {
    return request('/');
  },

  // Authentication
  async register(data) {
    return request('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async login(email, password) {
    return request('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  async getMe() {
    return request('/api/v1/auth/me');
  },

  // Expenses CRUD
  async getExpenses(params = {}) {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.type) query.append('type', params.type);
    if (params.search) query.append('search', params.search);
    if (params.start_date) query.append('start_date', params.start_date);
    if (params.end_date) query.append('end_date', params.end_date);
    if (params.skip !== undefined) query.append('skip', params.skip);
    if (params.limit !== undefined) query.append('limit', params.limit);

    const queryString = query.toString();
    const endpoint = `/api/v1/expenses${queryString ? `?${queryString}` : ''}`;
    return request(endpoint);
  },

  async getTotals() {
    return request('/api/v1/expenses/totals');
  },

  async getExpenseById(id) {
    return request(`/api/v1/expenses/${id}`);
  },

  async createExpense(expenseData) {
    return request('/api/v1/expenses', {
      method: 'POST',
      body: JSON.stringify(expenseData),
    });
  },

  async updateExpense(id, updateData) {
    return request(`/api/v1/expenses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    });
  },

  async deleteExpense(id) {
    return request(`/api/v1/expenses/${id}`, {
      method: 'DELETE',
    });
  },

  // Budgets
  async getBudgets(month, year) {
    const query = new URLSearchParams();
    if (month) query.append('month', month);
    if (year) query.append('year', year);
    const queryString = query.toString();
    return request(`/api/v1/budgets${queryString ? `?${queryString}` : ''}`);
  },

  async saveBudget(budgetData) {
    return request('/api/v1/budgets', {
      method: 'POST',
      body: JSON.stringify(budgetData),
    });
  },

  async deleteBudget(id) {
    return request(`/api/v1/budgets/${id}`, {
      method: 'DELETE',
    });
  },

  // Reports
  async getSummary(startDate, endDate) {
    const query = new URLSearchParams();
    if (startDate) query.append('start_date', startDate);
    if (endDate) query.append('end_date', endDate);
    const queryString = query.toString();
    return request(`/api/v1/reports/summary${queryString ? `?${queryString}` : ''}`);
  },

  async downloadCsv(startDate, endDate) {
    const query = new URLSearchParams();
    if (startDate) query.append('start_date', startDate);
    if (endDate) query.append('end_date', endDate);
    const queryString = query.toString();
    const url = `${API_BASE_URL}/api/v1/reports/export-csv${queryString ? `?${queryString}` : ''}`;

    const headers = getAuthHeaders();
    delete headers['Content-Type'];

    const response = await fetch(url, { headers });
    if (!response.ok) {
      throw new Error(`CSV export failed: ${response.statusText}`);
    }
    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `spendsense_export_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(downloadUrl);
  },

  // AI Assistant
  async askAI(message, history = []) {
    return request('/api/v1/ai/chat', {
      method: 'POST',
      body: JSON.stringify({ message, history }),
    });
  },
};
