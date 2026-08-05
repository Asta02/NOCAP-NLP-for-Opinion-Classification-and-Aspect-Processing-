export type CompanyStatus = 'active' | 'inactive' | 'pending';

export interface Company {
  company_id: number;
  company_name: string;
  industry: string;
  email: string;
  username: string;
  status: CompanyStatus;
  logo_url: string | null;
  created_at: string;
}

export interface CompanyFormData {
  company_name: string;
  industry: string;
  email: string;
  username: string;
  password?: string;
  logo_url?: string;
}

export interface CreateCompanyRequest {
  company_name: string;
  industry: string;
  email: string;
  username: string;
  password: string;
  logo_url?: string;
}

export interface UpdateCompanyRequest {
  company_name?: string;
  industry?: string;
  email?: string;
  username?: string;
  password?: string;
  logo_url?: string;
  status?: CompanyStatus;
}

export interface CompanyListParams {
  search?: string;
  status?: CompanyStatus;
  industry?: string;
  page?: number;
  limit?: number;
}

export interface CompanyListResponse {
  companies: Company[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}
