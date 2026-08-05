import { AdminReviewListParams, AdminReviewListResponse, CreateReviewRequest, Review, ReviewListParams, ReviewListResponse } from '@/types/review';
import { mockReviews, mockCompanies } from '@/services/mock/mock-data';

export interface IReviewService {
  getAll(params?: ReviewListParams): Promise<ReviewListResponse>;
  getAdminAll(params?: AdminReviewListParams): Promise<AdminReviewListResponse>;
  getById(id: number): Promise<Review>;
  create(data: CreateReviewRequest, companyId: number): Promise<Review>;
}

export class MockReviewService implements IReviewService {
  private reviews: Review[] = [...mockReviews];

  async getAll(params?: ReviewListParams): Promise<ReviewListResponse> {
    await this.simulateDelay();

    let filtered = [...this.reviews];

    if (params?.company_id) {
      filtered = filtered.filter((r) => r.company_id === params.company_id);
    }

    if (params?.search) {
      const search = params.search.toLowerCase();
      filtered = filtered.filter(
        (r) =>
          r.summary.toLowerCase().includes(search) ||
          r.job_title.toLowerCase().includes(search) ||
          r.review_text.toLowerCase().includes(search)
      );
    }

    if (params?.sentiment) {
      filtered = filtered.filter((r) => r.sentiment === params.sentiment);
    }

    if (params?.min_rating !== undefined) {
      filtered = filtered.filter((r) => r.overall_rating >= params.min_rating!);
    }

    if (params?.max_rating !== undefined) {
      filtered = filtered.filter((r) => r.overall_rating <= params.max_rating!);
    }

    if (params?.start_date) {
      filtered = filtered.filter((r) => r.review_date >= params.start_date!);
    }

    if (params?.end_date) {
      filtered = filtered.filter((r) => r.review_date <= params.end_date!);
    }

    filtered.sort((a, b) =>
      new Date(b.review_date).getTime() - new Date(a.review_date).getTime()
    );

    const page = params?.page || 1;
    const limit = params?.limit || 10;
    const total = filtered.length;
    const totalPages = Math.ceil(total / limit);
    const start = (page - 1) * limit;
    const paginatedData = filtered.slice(start, start + limit);

    return {
      reviews: paginatedData,
      total,
      page,
      limit,
      total_pages: totalPages,
    };
  }

  async getAdminAll(params?: AdminReviewListParams): Promise<AdminReviewListResponse> {
    await this.simulateDelay();

    let filtered = [...this.reviews];

    if (params?.company_name) {
      const search = params.company_name.toLowerCase();
      filtered = filtered.filter((r) =>
        r.company_name.toLowerCase().includes(search)
      );
    }

    if (params?.search) {
      const search = params.search.toLowerCase();
      filtered = filtered.filter(
        (r) =>
          r.summary.toLowerCase().includes(search) ||
          r.job_title.toLowerCase().includes(search) ||
          r.company_name.toLowerCase().includes(search)
      );
    }

    if (params?.sentiment) {
      filtered = filtered.filter((r) => r.sentiment === params.sentiment);
    }

    if (params?.start_date) {
      filtered = filtered.filter((r) => r.review_date >= params.start_date!);
    }

    if (params?.end_date) {
      filtered = filtered.filter((r) => r.review_date <= params.end_date!);
    }

    filtered.sort((a, b) =>
      new Date(b.review_date).getTime() - new Date(a.review_date).getTime()
    );

    const page = params?.page || 1;
    const limit = params?.limit || 10;
    const total = filtered.length;
    const totalPages = Math.ceil(total / limit);
    const start = (page - 1) * limit;
    const paginatedData = filtered.slice(start, start + limit);

    return {
      reviews: paginatedData,
      total,
      page,
      limit,
      total_pages: totalPages,
    };
  }

  async getById(id: number): Promise<Review> {
    await this.simulateDelay();
    const review = this.reviews.find((r) => r.review_id === id);
    if (!review) {
      throw new Error('Review not found');
    }
    return review;
  }

  async create(data: CreateReviewRequest, companyId: number): Promise<Review> {
    await this.simulateDelay();

    const company = mockCompanies.find((c) => c.company_id === companyId);

    const sentiment = this.calculateSentiment(data.overall_rating);

    const newReview: Review = {
      review_id: this.reviews.length + 1,
      company_id: companyId,
      company_name: company?.company_name || 'Unknown',
      review_date: data.review_date,
      employment_status: data.employment_status,
      job_title: data.job_title,
      summary: data.summary,
      review_text: data.review_text,
      overall_rating: data.overall_rating,
      work_life_balance: data.work_life_balance,
      culture_values: data.culture_values,
      career_opportunities: data.career_opportunities,
      compensation_benefits: data.compensation_benefits,
      senior_management: data.senior_management,
      sentiment,
      status: 'pending',
      created_at: new Date().toISOString().split('T')[0],
    };

    this.reviews.unshift(newReview);
    return newReview;
  }

  private calculateSentiment(rating: number): 'Positive' | 'Neutral' | 'Negative' {
    if (rating >= 4) return 'Positive';
    if (rating >= 3) return 'Neutral';
    return 'Negative';
  }

  private simulateDelay(ms?: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms || Math.random() * 400 + 200));
  }
}

export class RealReviewService implements IReviewService {
  async getAll(params?: ReviewListParams): Promise<ReviewListResponse> {
    const { apiGet } = await import('@/services/api');
    return apiGet<ReviewListResponse>('/reviews', { params });
  }

  async getAdminAll(params?: AdminReviewListParams): Promise<AdminReviewListResponse> {
    const { apiGet } = await import('@/services/api');
    return apiGet<AdminReviewListResponse>('/admin/reviews', { params });
  }

  async getById(id: number): Promise<Review> {
    const { apiGet } = await import('@/services/api');
    return apiGet<Review>(`/reviews/${id}`);
  }

  async create(data: CreateReviewRequest, companyId: number): Promise<Review> {
    const { apiPost } = await import('@/services/api');
    return apiPost<Review>('/reviews', { ...data, company_id: companyId });
  }
}
