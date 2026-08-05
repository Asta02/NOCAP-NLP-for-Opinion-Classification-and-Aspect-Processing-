export type SentimentType = 'Positive' | 'Neutral' | 'Negative';
export type EmploymentStatus = 'Current Employee' | 'Former Employee';
export type ReviewStatus = 'pending' | 'analyzed' | 'imported';

export interface Review {
  review_id: number;
  company_id: number;
  company_name: string;
  review_date: string;
  employment_status: EmploymentStatus;
  job_title: string;
  summary: string;
  review_text: string;
  overall_rating: number;
  work_life_balance: number;
  culture_values: number;
  career_opportunities: number;
  compensation_benefits: number;
  senior_management: number;
  sentiment: SentimentType;
  status: ReviewStatus;
  created_at: string;
}

export interface CreateReviewRequest {
  review_date: string;
  employment_status: EmploymentStatus;
  job_title: string;
  summary: string;
  review_text: string;
  overall_rating: number;
  work_life_balance: number;
  culture_values: number;
  career_opportunities: number;
  compensation_benefits: number;
  senior_management: number;
}

export interface ReviewListParams {
  search?: string;
  company_id?: number;
  sentiment?: SentimentType;
  status?: ReviewStatus;
  start_date?: string;
  end_date?: string;
  min_rating?: number;
  max_rating?: number;
  page?: number;
  limit?: number;
}

export interface ReviewListResponse {
  reviews: Review[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AdminReviewListParams extends ReviewListParams {
  company_name?: string;
}

export interface AdminReviewListResponse extends ReviewListResponse {}
