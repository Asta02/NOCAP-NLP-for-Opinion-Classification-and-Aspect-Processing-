import { Company, CompanyListParams, CompanyListResponse, CreateCompanyRequest, UpdateCompanyRequest } from '@/types/company';
import { mockCompanies } from '@/services/mock/mock-data';

export interface ICompanyService {
  getAll(params?: CompanyListParams): Promise<CompanyListResponse>;
  getById(id: number): Promise<Company>;
  create(data: CreateCompanyRequest): Promise<Company>;
  update(id: number, data: UpdateCompanyRequest): Promise<Company>;
  delete(id: number): Promise<void>;
  getIndustries(): Promise<string[]>;
}

export class MockCompanyService implements ICompanyService {
  private companies: Company[] = [...mockCompanies];
  private nextId = this.companies.length + 1;

  async getAll(params?: CompanyListParams): Promise<CompanyListResponse> {
    await this.simulateDelay();

    let filtered = [...this.companies];

    if (params?.search) {
      const search = params.search.toLowerCase();
      filtered = filtered.filter(
        (c: Company) =>
          c.company_name.toLowerCase().includes(search) ||
          c.industry.toLowerCase().includes(search) ||
          c.email.toLowerCase().includes(search)
      );
    }

    if (params?.status) {
      filtered = filtered.filter((c: Company) => c.status === params.status);
    }

    if (params?.industry) {
      filtered = filtered.filter((c: Company) => c.industry === params.industry);
    }

    filtered.sort((a: Company, b: Company) => a.company_name.localeCompare(b.company_name));

    const page = params?.page || 1;
    const limit = params?.limit || 10;
    const total = filtered.length;
    const totalPages = Math.ceil(total / limit);
    const start = (page - 1) * limit;
    const paginatedData = filtered.slice(start, start + limit);

    return {
      companies: paginatedData,
      total,
      page,
      limit,
      total_pages: totalPages,
    };
  }

  async getById(id: number): Promise<Company> {
    await this.simulateDelay();
    const company = this.companies.find((c: Company) => c.company_id === id);
    if (!company) {
      throw new Error('Company not found');
    }
    return company;
  }

  async create(data: CreateCompanyRequest): Promise<Company> {
    await this.simulateDelay();

    const newCompany: Company = {
      company_id: this.nextId++,
      company_name: data.company_name,
      industry: data.industry,
      email: data.email,
      username: data.username,
      status: 'pending',
      logo_url: data.logo_url || null,
      created_at: new Date().toISOString().split('T')[0],
    };

    this.companies.push(newCompany);
    return newCompany;
  }

  async update(id: number, data: UpdateCompanyRequest): Promise<Company> {
    await this.simulateDelay();

    const index = this.companies.findIndex((c: Company) => c.company_id === id);
    if (index === -1) {
      throw new Error('Company not found');
    }

    this.companies[index] = {
      ...this.companies[index],
      ...data,
    };

    return this.companies[index];
  }

  async delete(id: number): Promise<void> {
    await this.simulateDelay();

    const index = this.companies.findIndex((c: Company) => c.company_id === id);
    if (index === -1) {
      throw new Error('Company not found');
    }

    this.companies.splice(index, 1);
  }

  async getIndustries(): Promise<string[]> {
    await this.simulateDelay(200);
    const industries = new Set(this.companies.map((c) => c.industry));
    return Array.from(industries).sort() as string[];
  }

  private simulateDelay(ms?: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms || Math.random() * 400 + 200));
  }
}

export class RealCompanyService implements ICompanyService {
  async getAll(params?: CompanyListParams): Promise<CompanyListResponse> {
    const { apiGet } = await import('@/services/api');
    return apiGet<CompanyListResponse>('/admin/companies', { params });
  }

  async getById(id: number): Promise<Company> {
    const { apiGet } = await import('@/services/api');
    return apiGet<Company>(`/admin/companies/${id}`);
  }

  async create(data: CreateCompanyRequest): Promise<Company> {
    const { apiPost } = await import('@/services/api');
    return apiPost<Company>('/admin/companies', data);
  }

  async update(id: number, data: UpdateCompanyRequest): Promise<Company> {
    const { apiPut } = await import('@/services/api');
    return apiPut<Company>(`/admin/companies/${id}`, data);
  }

  async delete(id: number): Promise<void> {
    const { apiDelete } = await import('@/services/api');
    await apiDelete(`/admin/companies/${id}`);
  }

  async getIndustries(): Promise<string[]> {
    const { apiGet } = await import('@/services/api');
    return apiGet<string[]>('/industries');
  }
}
