import { LoginRequest, LoginResponse } from '@/types/auth';
import { mockCompanies } from '@/services/mock/mock-data';

export interface IAuthService {
  login(request: LoginRequest): Promise<LoginResponse>;
  logout(): Promise<void>;
}

export class MockAuthService implements IAuthService {
  async login(request: LoginRequest): Promise<LoginResponse> {
    await this.simulateDelay();

    const { username, password } = request;

    if (username === 'admin' && password === 'admin123') {
      return {
        token: 'mock_admin_token_' + Date.now(),
        role: 'admin',
      };
    }

    const company = mockCompanies.find(
      (c) => c.username.toLowerCase() === username.toLowerCase()
    );

    if (company && password === 'company123') {
      return {
        token: 'mock_company_token_' + Date.now(),
        role: 'company',
        company: {
          company_id: company.company_id,
          company_name: company.company_name,
        },
      };
    }

    throw new Error('Invalid username or password');
  }

  async logout(): Promise<void> {
    await this.simulateDelay(200);
  }

  private simulateDelay(ms?: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms || Math.random() * 500 + 300));
  }
}

export class RealAuthService implements IAuthService {
  async login(request: LoginRequest): Promise<LoginResponse> {
    const { apiPost } = await import('@/services/api');
    return apiPost<LoginResponse>('/auth/login', request);
  }

  async logout(): Promise<void> {
    const { apiPost } = await import('@/services/api');
    await apiPost('/auth/logout');
  }
}
