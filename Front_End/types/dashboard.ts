export interface DashboardOverview {
  total_reviews: number;
  average_rating: number;
  positive_reviews: number;
  neutral_reviews: number;
  negative_reviews: number;
}

export interface EmployeeMood {
  positive: number;
  neutral: number;
  negative: number;
}

export interface MonthlySentiment {
  month: string;
  positive: number;
  neutral: number;
  negative: number;
}

export interface RatingDistribution {
  rating: number;
  count: number;
}

export interface TopTopic {
  topic: string;
  count: number;
}

export interface KeywordScore {
  keyword: string;
  score: number;
}

export interface RecentReview {
  date: string;
  job_title: string;
  summary: string;
  rating: number;
  sentiment: 'Positive' | 'Neutral' | 'Negative';
}

export interface DashboardData {
  overview: DashboardOverview;
  employee_mood: EmployeeMood;
  monthly_sentiment: MonthlySentiment[];
  rating_distribution: RatingDistribution[];
  top_topics: TopTopic[];
  keywords: KeywordScore[];
  recent_reviews: RecentReview[];
}

export interface AdminDashboardData {
  total_companies: number;
  total_reviews: number;
  pending_jobs: number;
  completed_analysis: number;
  reviews_per_company: { company_name: string; count: number }[];
  monthly_imports: { month: string; count: number }[];
  processing_status: {
    pending: number;
    processing: number;
    completed: number;
    failed: number;
  };
  latest_uploads: {
    upload_id: number;
    company_name: string;
    filename: string;
    records: number;
    uploaded_at: string;
    status: string;
  }[];
}
