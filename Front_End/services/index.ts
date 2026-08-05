import { MockAuthService, RealAuthService } from './services/auth.service';
import { MockCompanyService, RealCompanyService } from './services/company.service';
import { MockReviewService, RealReviewService } from './services/review.service';
import { MockDashboardService, RealDashboardService } from './services/dashboard.service';
import { MockAiProcessingService, RealAiProcessingService } from './services/ai-processing.service';

export type { IAuthService } from './services/auth.service';
export type { ICompanyService } from './services/company.service';
export type { IReviewService } from './services/review.service';
export type { IDashboardService } from './services/dashboard.service';
export type { IAiProcessingService } from './services/ai-processing.service';

import type { IAuthService } from './services/auth.service';
import type { ICompanyService } from './services/company.service';
import type { IReviewService } from './services/review.service';
import type { IDashboardService } from './services/dashboard.service';
import type { IAiProcessingService } from './services/ai-processing.service';

const USE_MOCK = process.env.NEXT_PUBLIC_USE_MOCK !== 'false';

export const authService: IAuthService = USE_MOCK ? new MockAuthService() : new RealAuthService();
export const companyService: ICompanyService = USE_MOCK ? new MockCompanyService() : new RealCompanyService();
export const reviewService: IReviewService = USE_MOCK ? new MockReviewService() : new RealReviewService();
export const dashboardService: IDashboardService = USE_MOCK ? new MockDashboardService() : new RealDashboardService();
export const aiProcessingService: IAiProcessingService = USE_MOCK ? new MockAiProcessingService() : new RealAiProcessingService();
