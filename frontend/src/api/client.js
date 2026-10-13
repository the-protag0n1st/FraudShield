// FraudShield API Client

let csrfToken = null;

export function setCsrfToken(token) {
  csrfToken = token;
}

export function getCsrfToken() {
  return csrfToken;
}

export async function apiFetch(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (csrfToken && options.method && options.method.toUpperCase() !== 'GET') {
    headers['X-CSRF-Token'] = csrfToken;
  }

  const config = {
    credentials: 'include',
    ...options,
    headers
  };

  const response = await fetch(endpoint, config);

  let data;
  try {
    data = await response.json();
  } catch (err) {
    data = null;
  }

  if (!response.ok) {
    const errorMsg = data?.error || `Request failed with status ${response.status}`;
    const err = new Error(errorMsg);
    err.status = response.status;
    err.code = data?.code;
    throw err;
  }

  if (data?.csrf_token) {
    setCsrfToken(data.csrf_token);
  }

  return data;
}

// Authentication
export const authApi = {
  async getMe() {
    const res = await apiFetch('/api/auth/me');
    if (res.csrf_token) setCsrfToken(res.csrf_token);
    return res;
  },
  async login(email, password) {
    const res = await apiFetch('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    if (res.csrf_token) setCsrfToken(res.csrf_token);
    return res;
  },
  async logout() {
    return apiFetch('/api/auth/logout', { method: 'POST' });
  }
};

// Dashboard
export const dashboardApi = {
  getSummary: () => apiFetch('/api/dashboard/summary'),
  getTrends: () => apiFetch('/api/dashboard/trends')
};

// Transactions
export const transactionsApi = {
  getTransactions: (params = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.append(k, v);
    });
    return apiFetch(`/api/transactions?${q.toString()}`);
  },
  getTransaction: (id) => apiFetch(`/api/transactions/${id}`),
  createTransaction: (data) => apiFetch('/api/transactions', {
    method: 'POST',
    body: JSON.stringify(data)
  }),
  reassess: (id) => apiFetch(`/api/transactions/${id}/assess`, { method: 'POST' }),
  triggerScenario: (scenario) => apiFetch('/api/transactions/demo/scenario', {
    method: 'POST',
    body: JSON.stringify({ scenario })
  })
};

// Cases
export const casesApi = {
  getCases: (params = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.append(k, v);
    });
    return apiFetch(`/api/cases?${q.toString()}`);
  },
  getCase: (id) => apiFetch(`/api/cases/${id}`),
  updateCase: (id, data) => apiFetch(`/api/cases/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(data)
  }),
  addNote: (id, noteText) => apiFetch(`/api/cases/${id}/notes`, {
    method: 'POST',
    body: JSON.stringify({ note_text: noteText })
  })
};

// Analytics
export const analyticsApi = {
  getOverview: () => apiFetch('/api/analytics/overview'),
  getRiskDistribution: () => apiFetch('/api/analytics/risk-distribution'),
  getTopMerchants: () => apiFetch('/api/analytics/top-merchants'),
  getResolutionRates: () => apiFetch('/api/analytics/resolution-rates')
};

// Admin & Entity Lookups
export const adminApi = {
  getAuditLogs: (params = {}) => {
    const q = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') q.append(k, v);
    });
    return apiFetch(`/api/admin/audit-logs?${q.toString()}`);
  },
  getUsers: () => apiFetch('/api/users'),
  getCustomers: () => apiFetch('/api/customers'),
  getMerchants: () => apiFetch('/api/merchants')
};
