const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// Auth
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  role?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    full_name?: string;
    role: string;
    is_active: boolean;
  };
}

// Knowledge
export interface SearchRequest {
  query: string;
  top_k?: number;
  use_hybrid_search?: boolean;
  filters?: Record<string, any>;
}

export interface SearchSource {
  chunk_id: string;
  content: string;
  similarity: number;
  combined_score?: number;
  metadata: string;
  metadata_parsed?: Record<string, any>;
  document_id: string;
}

export interface SearchResponse {
  answer: string;
  sources: SearchSource[];
  confidence: string;
  context_used: number;
  intent?: string;
  entities?: Record<string, any>;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  document_type: string;
  source_url?: string;
  source_name?: string;
  authority_level: string;
  status: string;
  created_at: string;
}

// Products
export interface ProductCreate {
  name: string;
  description?: string;
  category: string;
  sku?: string;
  brand?: string;
  model?: string;
  specifications?: Record<string, any>;
  intended_use?: string;
  target_market?: string;
}

export interface Product {
  id: string;
  name: string;
  description?: string;
  category: string;
  sku?: string;
  brand?: string;
  model?: string;
  specifications?: Record<string, any>;
  intended_use?: string;
  target_market?: string;
  status: string;
  created_at: string;
}

export interface ProductStandardMatch {
  id: string;
  product_id: string;
  standard_id: string;
  match_score?: number;
  match_reason?: string;
  is_mandatory: string;
  applicability_notes?: string;
}

export interface ComplianceCheckCreate {
  standard_id: string;
  check_type?: string;
}

export interface ComplianceCheck {
  id: string;
  product_id: string;
  standard_id: string;
  check_type: string;
  status: string;
  overall_score?: number;
  checked_at?: string;
  notes?: string;
}

// Labs
export interface Lab {
  id: string;
  name: string;
  lab_type?: string;
  city?: string;
  state?: string;
  country?: string;
  contact_email?: string;
  contact_phone?: string;
  website?: string;
  nabl_accreditation_number?: string;
  bis_recognition_number?: string;
  scope_of_testing?: string;
  capabilities?: string[];
  verification_status?: string;
  authority_level?: string;
}

export interface LabSearchResponse {
  total: number;
  labs: Lab[];
  note: string;
}

// Document Analysis
export interface DocumentAnalysisResponse {
  filename: string;
  file_size: number;
  text_extracted: boolean;
  text_length?: number;
  is_numbers_found?: string[];
  standards_found?: string[];
  analysis?: {
    answer: string;
    confidence: string;
    sources: SearchSource[];
    intent?: string;
  };
  error?: string;
  disclaimer?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Always read token fresh from localStorage — fixes the "token not sent after login" bug
  private getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  setToken(token: string) {
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    localStorage.removeItem('access_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        return { error: data.detail || `Request failed (${response.status})` };
      }

      return { data };
    } catch (error) {
      return { error: 'Network error — is the backend running?' };
    }
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    return this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  async register(userData: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    return this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(): Promise<ApiResponse<AuthResponse['user']>> {
    return this.request<AuthResponse['user']>('/auth/me');
  }

  // Knowledge endpoints
  async searchKnowledge(query: SearchRequest): Promise<ApiResponse<SearchResponse>> {
    return this.request<SearchResponse>('/knowledge/search', {
      method: 'POST',
      body: JSON.stringify(query),
    });
  }

  async listDocuments(): Promise<ApiResponse<KnowledgeDocument[]>> {
    return this.request<KnowledgeDocument[]>('/knowledge/documents');
  }

  // Product endpoints
  async createProduct(product: ProductCreate): Promise<ApiResponse<Product>> {
    return this.request<Product>('/products/', {
      method: 'POST',
      body: JSON.stringify(product),
    });
  }

  async listProducts(): Promise<ApiResponse<Product[]>> {
    return this.request<Product[]>('/products/');
  }

  async getProduct(productId: string): Promise<ApiResponse<Product>> {
    return this.request<Product>(`/products/${productId}`);
  }

  async matchStandards(productId: string): Promise<ApiResponse<ProductStandardMatch[]>> {
    return this.request<ProductStandardMatch[]>(`/products/${productId}/match-standards`, {
      method: 'POST',
    });
  }

  async getProductMatches(productId: string): Promise<ApiResponse<ProductStandardMatch[]>> {
    return this.request<ProductStandardMatch[]>(`/products/${productId}/matches`);
  }

  async createComplianceCheck(
    productId: string,
    checkData: ComplianceCheckCreate
  ): Promise<ApiResponse<ComplianceCheck>> {
    return this.request<ComplianceCheck>(`/products/${productId}/compliance-checks`, {
      method: 'POST',
      body: JSON.stringify(checkData),
    });
  }

  async getComplianceSummary(productId: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/products/${productId}/compliance-checks`);
  }

  // Lab endpoints
  async searchLabs(params?: {
    q?: string;
    city?: string;
    lab_type?: string;
  }): Promise<ApiResponse<LabSearchResponse>> {
    const qs = new URLSearchParams();
    if (params?.q) qs.set('q', params.q);
    if (params?.city) qs.set('city', params.city);
    if (params?.lab_type) qs.set('lab_type', params.lab_type);
    const query = qs.toString() ? `?${qs.toString()}` : '';
    return this.request<LabSearchResponse>(`/labs/${query}`);
  }

  // Document analysis
  async analyzeDocument(file: File): Promise<ApiResponse<DocumentAnalysisResponse>> {
    const token = this.getToken();
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    // Do NOT set Content-Type — let browser set multipart boundary
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${this.baseUrl}/documents/analyze`, {
        method: 'POST',
        headers,
        body: formData,
      });
      const data = await response.json();
      if (!response.ok) {
        return { error: data.detail || `Analysis failed (${response.status})` };
      }
      return { data };
    } catch (error) {
      return { error: 'Network error — is the backend running?' };
    }
  }
}

export const apiClient = new ApiClient();
