import { AdminDashboardData, DashboardData } from '@/types/dashboard';
import { DecisionSupportData } from '@/types/decision-support';
import {
  generateCompanyDashboardData,
  generateMockAdminDashboard,
  generateDecisionSupportData,
} from '@/services/mock/mock-data';

export interface IDashboardService {
  getCompanyDashboard(companyId: number): Promise<DashboardData>;
  getAdminDashboard(): Promise<AdminDashboardData>;
  getDecisionSupport(companyId: number): Promise<DecisionSupportData>;
}

export class MockDashboardService implements IDashboardService {
  async getCompanyDashboard(companyId: number): Promise<DashboardData> {
    await this.simulateDelay();
    return generateCompanyDashboardData(companyId);
  }

  async getAdminDashboard(): Promise<AdminDashboardData> {
    await this.simulateDelay();
    return generateMockAdminDashboard();
  }

  async getDecisionSupport(companyId: number): Promise<DecisionSupportData> {
    await this.simulateDelay();
    return generateDecisionSupportData(companyId);
  }

  private simulateDelay(ms?: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms || Math.random() * 600 + 400));
  }
}

export class RealDashboardService implements IDashboardService {
  async getCompanyDashboard(companyId: number): Promise<DashboardData> {
    const { apiGet } = await import('@/services/api');
    return apiGet<DashboardData>('/dashboard', { params: { company_id: companyId } });
  }

  async getAdminDashboard(): Promise<AdminDashboardData> {
    const { apiGet } = await import('@/services/api');
    return apiGet<AdminDashboardData>('/admin/dashboard');
  }

  async getDecisionSupport(companyId: number): Promise<DecisionSupportData> {
    const { apiGet } = await import('@/services/api');
    return apiGet<DecisionSupportData>('/dashboard/decision-support', { params: { company_id: companyId } });
  }
}
