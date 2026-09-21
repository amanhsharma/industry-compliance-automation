const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export interface User {
  id: string;
  tenant_id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  tenant?: {
    id: string;
    name: string;
    slug: string;
  };
}

export interface DashboardSummary {
  total_records: number;
  total_datasets: number;
  total_violations: number;
  open_violations: number;
  under_review_violations: number;
  resolved_violations: number;
  compliance_score: number;
  severity_breakdown: { severity: string; count: number }[];
  status_breakdown: { status: string; count: number }[];
  rule_distribution: { rule_code: string; rule_name: string; severity: string; count: number }[];
  trends: { date: string; violations: number; clean_records: number }[];
}

export interface Violation {
  id: string;
  tenant_id: string;
  dataset_id: string;
  record_id: string;
  rule_code: string;
  rule_name: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  status: "OPEN" | "UNDER_REVIEW" | "RESOLVED";
  message: string;
  details_json: string;
  auditor_notes?: string;
  assigned_to?: string;
  resolved_at?: string;
  created_at: string;
  record?: {
    transaction_id: string;
    account_id: string;
    counterparty_name?: string;
    counterparty_country?: string;
    amount: number;
    currency: string;
    timestamp?: string;
    kyc_status: string;
    transaction_type: string;
  };
}

export interface Dataset {
  id: string;
  tenant_id: string;
  filename: string;
  file_size_bytes: number;
  row_count: number;
  violation_count: number;
  status: string;
  created_at: string;
}

export interface ComplianceRule {
  id: string;
  code: string;
  name: string;
  description: string;
  category: string;
  severity: string;
  regulatory_framework: string;
  parameters_json: string;
  is_active: boolean;
  created_at: string;
}

function getAuthHeader(): HeadersInit {
  const token = localStorage.getItem("apex_access_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function safeFetch(url: string, options?: RequestInit): Promise<Response> {
  try {
    const res = await fetch(url, options);
    return res;
  } catch (err: any) {
    if (err.name === "TypeError" && err.message.includes("fetch")) {
      throw new Error("Unable to connect to backend server at http://localhost:8000. Please ensure backend is running.");
    }
    throw err;
  }
}

export const api = {
  async login(email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await safeFetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Login failed");
    }
    const data = await res.json();
    localStorage.setItem("apex_access_token", data.access_token);
    return data;
  },

  async register(tenant_name: string, full_name: string, email: string, password: string): Promise<{ access_token: string; user: User }> {
    const res = await safeFetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tenant_name, full_name, email, password }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(err.detail || "Registration failed");
    }
    const data = await res.json();
    localStorage.setItem("apex_access_token", data.access_token);
    return data;
  },

  async getMe(): Promise<User> {
    const res = await safeFetch(`${API_BASE_URL}/auth/me`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error("Unauthorized");
    return res.json();
  },

  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await safeFetch(`${API_BASE_URL}/dashboard/summary`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error("Failed to load dashboard summary");
    return res.json();
  },

  async listViolations(filters?: { severity?: string; status?: string; search?: string }): Promise<Violation[]> {
    const params = new URLSearchParams();
    if (filters?.severity) params.append("severity", filters.severity);
    if (filters?.status) params.append("status", filters.status);
    if (filters?.search) params.append("search", filters.search);

    const res = await safeFetch(`${API_BASE_URL}/violations?${params.toString()}`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error("Failed to load violations");
    return res.json();
  },

  async updateViolation(id: string, update: { status?: string; auditor_notes?: string }): Promise<Violation> {
    const res = await safeFetch(`${API_BASE_URL}/violations/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify(update),
    });
    if (!res.ok) throw new Error("Failed to update violation");
    return res.json();
  },

  async uploadCsv(file: File): Promise<Dataset> {
    const formData = new FormData();
    formData.append("file", file);

    const res = await safeFetch(`${API_BASE_URL}/datasets/upload`, {
      method: "POST",
      headers: { ...getAuthHeader() },
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }
    return res.json();
  },

  async listDatasets(): Promise<Dataset[]> {
    const res = await safeFetch(`${API_BASE_URL}/datasets`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error("Failed to list datasets");
    return res.json();
  },

  async listRules(): Promise<ComplianceRule[]> {
    const res = await safeFetch(`${API_BASE_URL}/rules`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error("Failed to load compliance rules");
    return res.json();
  },

  async toggleRule(ruleId: string, isActive: boolean): Promise<ComplianceRule> {
    const res = await safeFetch(`${API_BASE_URL}/rules/${ruleId}/toggle`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeader(),
      },
      body: JSON.stringify({ is_active: isActive }),
    });
    if (!res.ok) throw new Error("Failed to toggle rule state");
    return res.json();
  },

  async downloadReportPdf(): Promise<Blob> {
    const res = await safeFetch(`${API_BASE_URL}/reports/pdf`, {
      headers: { ...getAuthHeader() },
    });
    if (!res.ok) throw new Error("Failed to generate PDF report");
    return res.blob();
  },
};
