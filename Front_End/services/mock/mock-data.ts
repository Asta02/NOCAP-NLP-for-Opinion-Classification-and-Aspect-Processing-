import { Company } from '@/types/company';
import { Review } from '@/types/review';
import { AiProcessingJob } from '@/types/ai-processing';
import { DashboardData, AdminDashboardData } from '@/types/dashboard';
import { DecisionSupportData } from '@/types/decision-support';

const industries = [
  'Technology',
  'E-Commerce',
  'Financial Services',
  'Healthcare',
  'Manufacturing',
  'Retail',
  'Consulting',
  'Media & Entertainment',
  'Automotive',
  'Telecommunications',
];

const statuses: Array<'active' | 'inactive' | 'pending'> = ['active', 'inactive', 'pending'];

const jobTitles = [
  'Software Engineer',
  'Senior Software Engineer',
  'Software Developer',
  'Full Stack Developer',
  'Frontend Developer',
  'Backend Developer',
  'DevOps Engineer',
  'Data Scientist',
  'Product Manager',
  'Project Manager',
  'Engineering Manager',
  'Technical Lead',
  'QA Engineer',
  'UX Designer',
  'UI Designer',
  'Data Analyst',
  'Business Analyst',
  'Marketing Manager',
  'Sales Representative',
  'Customer Success Manager',
  'Human Resources Manager',
  'Financial Analyst',
  'Operations Manager',
  'Supply Chain Analyst',
  'Quality Assurance Manager',
];

const positiveSummaries = [
  'Great company with excellent growth opportunities',
  'Amazing work culture and supportive leadership',
  'Best place I have ever worked',
  'Innovative environment with talented colleagues',
  'Strong company values and mission',
  'Excellent compensation and benefits package',
  'Great work-life balance and flexibility',
  'Supportive management and clear career path',
  'Collaborative team environment',
  'Fantastic learning and development opportunities',
];

const neutralSummaries = [
  'Decent workplace with room for improvement',
  'Good benefits but management needs work',
  'Average experience overall',
  'Some good teams, some not so good',
  'Mixed feelings about the company direction',
  'Stable job but limited growth',
  'Okay place to start your career',
  'Fair compensation but high workload',
];

const negativeSummaries = [
  'Poor management and lack of direction',
  'Toxic work environment',
  'Underpaid and overworked',
  'No work-life balance',
  'Limited career advancement opportunities',
  'High turnover and low morale',
  'Communication issues across departments',
  'Micromanagement and lack of trust',
];

const positiveReviewTexts = [
  "I have been working at this company for over three years and it has been an incredible journey. The leadership team genuinely cares about employee well-being and professional development. Work-life balance is respected, and there are plenty of opportunities to learn and grow. The collaborative culture makes it easy to share ideas and innovate. Benefits are comprehensive including health insurance, retirement plans, and generous PTO. I highly recommend this company to anyone looking for a supportive and dynamic workplace.",
  "This is hands down the best company I have worked for. The culture here is exceptional - everyone is supportive, intelligent, and driven. Management is transparent and communicative. They truly invest in their employees through training programs, mentorship opportunities, and clear career progression paths. The flexible work arrangements and remote options have made a huge difference in my quality of life. Compensation is competitive and the bonus structure rewards performance fairly.",
  "Amazing place to build a career. The projects are challenging and meaningful, and you get to work with talented people who are always willing to help. The company values work-life balance and provides excellent benefits. Regular team events and company-wide initiatives make you feel part of a community. Career growth is supported through internal mobility and promotion opportunities. I started as a junior developer and have been promoted twice in two years.",
];

const neutralReviewTexts = [
  "The company has its strengths and weaknesses. On the positive side, the benefits package is decent, and the work schedule is fairly predictable. The team I work with is supportive, though communication from upper management could be better. There are some opportunities for advancement, but they seem to favor certain departments over others. The pay is average for the industry, and the work can become repetitive. Overall, it is a stable place to work but may not be the best for those seeking rapid career growth.",
  "My experience has been mixed. Some managers are excellent and truly invested in their team's success, while others seem disconnected from day-to-day operations. The work itself is interesting, but processes can be bureaucratic and slow. Work-life balance varies by team - some have it great while others struggle with workload. Compensation and benefits are adequate but could be more competitive. The company is trying to improve culture, but change is slow.",
];

const negativeReviewTexts = [
  "I cannot recommend this company. Management is disconnected from the reality of day-to-day work and makes decisions without considering employee input. There is a culture of overwork where long hours are expected without recognition or compensation. Promotions seem based on favoritism rather than merit. Communication is poor, and important information often does not reach employees until the last minute. The talented people I started with have mostly left for better opportunities. High turnover should be a red flag.",
  "The work environment here is toxic. There is constant pressure to deliver with unrealistic deadlines. Micromanagement is the norm, and there is no trust in employees. Despite promises of work-life balance, you are expected to be available around the clock. The compensation does not justify the stress and hours. HR does not take concerns seriously. I have seen many colleagues burn out and leave. Think carefully before joining.",
];

function generateRandomDate(start: Date, end: Date): string {
  const date = new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime()));
  return date.toISOString().split('T')[0];
}

function generateRandomRating(min: number, max: number): number {
  return Math.round((Math.random() * (max - min) + min) * 10) / 10;
}

function generateReviews(companies: Company[]): Review[] {
  const reviews: Review[] = [];
  let reviewId = 1;

  companies.forEach((company) => {
    const reviewsCount = Math.floor(Math.random() * 80) + 20;

    for (let i = 0; i < reviewsCount; i++) {
      const isPositive = Math.random() > 0.25;
      const isNeutral = Math.random() > 0.85;
      const jobTitle = jobTitles[Math.floor(Math.random() * jobTitles.length)];
      const employmentStatus: 'Current Employee' | 'Former Employee' =
        Math.random() > 0.3 ? 'Current Employee' : 'Former Employee';

      let summary: string;
      let reviewText: string;
      let sentiment: 'Positive' | 'Neutral' | 'Negative';
      let overallRating: number;
      let baseRatings: { wlb: number; culture: number; career: number; comp: number; mgmt: number };

      if (isNeutral) {
        summary = neutralSummaries[Math.floor(Math.random() * neutralSummaries.length)];
        reviewText = neutralReviewTexts[Math.floor(Math.random() * neutralReviewTexts.length)];
        sentiment = 'Neutral';
        overallRating = generateRandomRating(2.5, 3.5);
        baseRatings = {
          wlb: generateRandomRating(2.5, 3.5),
          culture: generateRandomRating(2.5, 3.5),
          career: generateRandomRating(2.5, 3.5),
          comp: generateRandomRating(2.5, 3.8),
          mgmt: generateRandomRating(2.5, 3.5),
        };
      } else if (isPositive) {
        summary = positiveSummaries[Math.floor(Math.random() * positiveSummaries.length)];
        reviewText = positiveReviewTexts[Math.floor(Math.random() * positiveReviewTexts.length)];
        sentiment = 'Positive';
        overallRating = generateRandomRating(3.8, 5.0);
        baseRatings = {
          wlb: generateRandomRating(3.5, 5.0),
          culture: generateRandomRating(3.8, 5.0),
          career: generateRandomRating(3.5, 5.0),
          comp: generateRandomRating(3.2, 4.8),
          mgmt: generateRandomRating(3.5, 5.0),
        };
      } else {
        summary = negativeSummaries[Math.floor(Math.random() * negativeSummaries.length)];
        reviewText = negativeReviewTexts[Math.floor(Math.random() * negativeReviewTexts.length)];
        sentiment = 'Negative';
        overallRating = generateRandomRating(1.0, 2.5);
        baseRatings = {
          wlb: generateRandomRating(1.0, 2.8),
          culture: generateRandomRating(1.0, 2.5),
          career: generateRandomRating(1.0, 2.5),
          comp: generateRandomRating(1.0, 2.8),
          mgmt: generateRandomRating(1.0, 2.5),
        };
      }

      reviews.push({
        review_id: reviewId++,
        company_id: company.company_id,
        company_name: company.company_name,
        review_date: generateRandomDate(new Date('2023-01-01'), new Date('2024-12-31')),
        employment_status: employmentStatus,
        job_title: jobTitle,
        summary,
        review_text: reviewText,
        overall_rating: Math.round(overallRating),
        work_life_balance: Math.round(baseRatings.wlb),
        culture_values: Math.round(baseRatings.culture),
        career_opportunities: Math.round(baseRatings.career),
        compensation_benefits: Math.round(baseRatings.comp),
        senior_management: Math.round(baseRatings.mgmt),
        sentiment,
        status: 'analyzed',
        created_at: generateRandomDate(new Date('2023-01-01'), new Date('2024-12-31')),
      });
    }
  });

  return reviews;
}

export function generateMockCompanies(): Company[] {
  const companyNames = [
    { name: 'Amazon', industry: 'E-Commerce' },
    { name: 'Google', industry: 'Technology' },
    { name: 'Microsoft', industry: 'Technology' },
    { name: 'Apple', industry: 'Technology' },
    { name: 'Meta', industry: 'Technology' },
    { name: 'Netflix', industry: 'Media & Entertainment' },
    { name: 'Salesforce', industry: 'Technology' },
    { name: 'Adobe', industry: 'Technology' },
    { name: 'Oracle', industry: 'Technology' },
    { name: 'IBM', industry: 'Technology' },
    { name: 'Intel', industry: 'Technology' },
    { name: 'Cisco', industry: 'Telecommunications' },
    { name: 'JPMorgan Chase', industry: 'Financial Services' },
    { name: 'Goldman Sachs', industry: 'Financial Services' },
    { name: 'Bank of America', industry: 'Financial Services' },
    { name: 'Johnson & Johnson', industry: 'Healthcare' },
    { name: 'Pfizer', industry: 'Healthcare' },
    { name: 'UnitedHealth Group', industry: 'Healthcare' },
    { name: 'Tesla', industry: 'Automotive' },
    { name: 'Ford', industry: 'Automotive' },
    { name: 'Boeing', industry: 'Manufacturing' },
    { name: 'General Electric', industry: 'Manufacturing' },
    { name: 'Walmart', industry: 'Retail' },
    { name: 'Target', industry: 'Retail' },
    { name: 'Deloitte', industry: 'Consulting' },
  ];

  const logos: Record<string, string> = {
    Amazon: 'https://logo.clearbit.com/amazon.com',
    Google: 'https://logo.clearbit.com/google.com',
    Microsoft: 'https://logo.clearbit.com/microsoft.com',
    Apple: 'https://logo.clearbit.com/apple.com',
    Meta: 'https://logo.clearbit.com/meta.com',
    Netflix: 'https://logo.clearbit.com/netflix.com',
    Salesforce: 'https://logo.clearbit.com/salesforce.com',
    Adobe: 'https://logo.clearbit.com/adobe.com',
    Oracle: 'https://logo.clearbit.com/oracle.com',
    IBM: 'https://logo.clearbit.com/ibm.com',
    Intel: 'https://logo.clearbit.com/intel.com',
    Cisco: 'https://logo.clearbit.com/cisco.com',
    'JPMorgan Chase': 'https://logo.clearbit.com/jpmorganchase.com',
    'Goldman Sachs': 'https://logo.clearbit.com/goldmansachs.com',
    'Bank of America': 'https://logo.clearbit.com/bankofamerica.com',
    'Johnson & Johnson': 'https://logo.clearbit.com/jnj.com',
    Pfizer: 'https://logo.clearbit.com/pfizer.com',
    'UnitedHealth Group': 'https://logo.clearbit.com/unitedhealthgroup.com',
    Tesla: 'https://logo.clearbit.com/tesla.com',
    Ford: 'https://logo.clearbit.com/ford.com',
    Boeing: 'https://logo.clearbit.com/boeing.com',
    'General Electric': 'https://logo.clearbit.com/ge.com',
    Walmart: 'https://logo.clearbit.com/walmart.com',
    Target: 'https://logo.clearbit.com/target.com',
    Deloitte: 'https://logo.clearbit.com/deloitte.com',
  };

  return companyNames.map((company, index) => ({
    company_id: index + 1,
    company_name: company.name,
    industry: company.industry,
    email: `contact@${company.name.toLowerCase().replace(/[^a-z0-9]/g, '')}.com`,
    username: company.name.toLowerCase().replace(/[^a-z0-9]/g, ''),
    status: statuses[index % 3] as 'active' | 'inactive' | 'pending',
    logo_url: logos[company.name] || null,
    created_at: generateRandomDate(new Date('2020-01-01'), new Date('2023-12-31')),
  }));
}

export const mockCompanies = generateMockCompanies();
export const mockReviews = generateReviews(mockCompanies);

export function generateMockAdminDashboard(): AdminDashboardData {
  const totalReviews = mockReviews.length;
  const totalCompanies = mockCompanies.filter((c) => c.status === 'active').length;

  const reviewsPerCompany = mockCompanies
    .filter((c) => c.status === 'active')
    .slice(0, 10)
    .map((company) => ({
      company_name: company.company_name,
      count: mockReviews.filter((r) => r.company_id === company.company_id).length,
    }))
    .sort((a, b) => b.count - a.count);

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const monthlyImports = months.map((month) => ({
    month,
    count: Math.floor(Math.random() * 150) + 50,
  }));

  return {
    total_companies: totalCompanies,
    total_reviews: totalReviews,
    pending_jobs: Math.floor(Math.random() * 5) + 2,
    completed_analysis: Math.floor(totalReviews * 0.85),
    reviews_per_company: reviewsPerCompany,
    monthly_imports: monthlyImports,
    processing_status: {
      pending: 12,
      processing: 3,
      completed: 156,
      failed: 2,
    },
    latest_uploads: [
      {
        upload_id: 1,
        company_name: 'Google',
        filename: 'employee_feedback_q4_2024.csv',
        records: 245,
        uploaded_at: '2024-12-15T10:30:00Z',
        status: 'completed',
      },
      {
        upload_id: 2,
        company_name: 'Microsoft',
        filename: 'annual_survey_2024.csv',
        records: 512,
        uploaded_at: '2024-12-14T14:20:00Z',
        status: 'processing',
      },
      {
        upload_id: 3,
        company_name: 'Amazon',
        filename: 'engagement_survey.csv',
        records: 1024,
        uploaded_at: '2024-12-13T09:15:00Z',
        status: 'completed',
      },
      {
        upload_id: 4,
        company_name: 'Meta',
        filename: 'feedback_q3_2024.csv',
        records: 320,
        uploaded_at: '2024-12-12T16:45:00Z',
        status: 'completed',
      },
      {
        upload_id: 5,
        company_name: 'Apple',
        filename: 'team_feedback.csv',
        records: 180,
        uploaded_at: '2024-12-11T11:00:00Z',
        status: 'failed',
      },
    ],
  };
}

export function generateCompanyDashboardData(companyId: number): DashboardData {
  const companyReviews = mockReviews.filter((r) => r.company_id === companyId);
  const totalReviews = companyReviews.length;

  const positiveReviews = companyReviews.filter((r) => r.sentiment === 'Positive').length;
  const neutralReviews = companyReviews.filter((r) => r.sentiment === 'Neutral').length;
  const negativeReviews = companyReviews.filter((r) => r.sentiment === 'Negative').length;

  const avgRating =
    totalReviews > 0
      ? Math.round(
          (companyReviews.reduce((sum, r) => sum + r.overall_rating, 0) / totalReviews) * 10
        ) / 10
      : 0;

  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const monthlySentiment = months.map((month) => {
    const basePositive = Math.random() * 20 + 60;
    const baseNeutral = Math.random() * 10 + 15;
    const baseNegative = 100 - basePositive - baseNeutral;
    return {
      month,
      positive: Math.round(basePositive),
      neutral: Math.round(baseNeutral),
      negative: Math.round(baseNegative),
    };
  });

  const ratingDistribution = [1, 2, 3, 4, 5].map((rating) => ({
    rating,
    count: companyReviews.filter((r) => r.overall_rating === rating).length,
  }));

  const topTopics = [
    { topic: 'Management', count: Math.floor(Math.random() * 100) + 80 },
    { topic: 'Career Growth', count: Math.floor(Math.random() * 80) + 60 },
    { topic: 'Work-Life Balance', count: Math.floor(Math.random() * 70) + 50 },
    { topic: 'Compensation', count: Math.floor(Math.random() * 60) + 40 },
    { topic: 'Benefits', count: Math.floor(Math.random() * 50) + 30 },
    { topic: 'Culture', count: Math.floor(Math.random() * 45) + 25 },
    { topic: 'Communication', count: Math.floor(Math.random() * 40) + 20 },
    { topic: 'Work Environment', count: Math.floor(Math.random() * 35) + 15 },
  ].sort((a, b) => b.count - a.count);

  const keywords = [
    { keyword: 'salary', score: 0.95 },
    { keyword: 'work-life balance', score: 0.92 },
    { keyword: 'management', score: 0.88 },
    { keyword: 'career growth', score: 0.85 },
    { keyword: 'communication', score: 0.82 },
    { keyword: 'benefits', score: 0.78 },
    { keyword: 'workload', score: 0.75 },
    { keyword: 'flexibility', score: 0.72 },
    { keyword: 'team', score: 0.68 },
    { keyword: 'leadership', score: 0.65 },
  ];

  const recentReviews = companyReviews
    .sort((a, b) => new Date(b.review_date).getTime() - new Date(a.review_date).getTime())
    .slice(0, 5)
    .map((r) => ({
      date: r.review_date,
      job_title: r.job_title,
      summary: r.summary,
      rating: r.overall_rating,
      sentiment: r.sentiment,
    }));

  return {
    overview: {
      total_reviews: totalReviews,
      average_rating: avgRating,
      positive_reviews: positiveReviews,
      neutral_reviews: neutralReviews,
      negative_reviews: negativeReviews,
    },
    employee_mood: {
      positive: totalReviews > 0 ? Math.round((positiveReviews / totalReviews) * 100) : 0,
      neutral: totalReviews > 0 ? Math.round((neutralReviews / totalReviews) * 100) : 0,
      negative: totalReviews > 0 ? Math.round((negativeReviews / totalReviews) * 100) : 0,
    },
    monthly_sentiment: monthlySentiment,
    rating_distribution: ratingDistribution,
    top_topics: topTopics,
    keywords: keywords,
    recent_reviews: recentReviews,
  };
}

export function generateDecisionSupportData(companyId: number): DecisionSupportData {
  const companyReviews = mockReviews.filter((r) => r.company_id === companyId);
  const positiveRatio =
    companyReviews.length > 0
      ? companyReviews.filter((r) => r.sentiment === 'Positive').length / companyReviews.length
      : 0.5;

  const healthScore = Math.round(positiveRatio * 100);

  let satisfaction: 'High' | 'Medium' | 'Low';
  if (healthScore >= 70) {
    satisfaction = 'High';
  } else if (healthScore >= 50) {
    satisfaction = 'Medium';
  } else {
    satisfaction = 'Low';
  }

  const companyName = mockCompanies.find((c) => c.company_id === companyId)?.company_name || 'the company';

  const executiveSummaries = {
    High: `Employee sentiment at ${companyName} is predominantly positive. Employees consistently appreciate the strong career development opportunities and healthy work-life balance. The company culture fosters collaboration and innovation, with leadership demonstrating genuine commitment to employee well-being. While minor areas exist for improvement in cross-departmental communication, the overall organizational health is excellent. Management should continue investing in professional development programs while maintaining the flexible working arrangements that employees value highly.`,
    Medium: `Employee sentiment at ${companyName} shows a mixed but generally stable outlook. While employees appreciate the competitive compensation and benefits packages, there are notable concerns about career advancement transparency and communication from middle management. The work environment varies significantly across teams, with some departments demonstrating stronger engagement than others. Key opportunities for improvement include implementing more structured career paths and improving leadership communication channels. Addressing these areas would significantly enhance overall employee satisfaction.`,
    Low: `Employee sentiment at ${companyName} indicates significant organizational challenges that require immediate attention. The primary concerns revolve around leadership communication, excessive workload expectations, and a lack of career development visibility. Employees report feeling undervalued and disconnected from company strategy. Urgent action is recommended to address these fundamental issues through transparent leadership engagement, workload rebalancing, and establishing clear promotion criteria. Without intervention, employee turnover risks remain high.`,
  };

  const strengthsSets = {
    High: [
      'Career Growth & Development',
      'Work-Life Balance',
      'Company Culture & Values',
      'Competitive Compensation',
      'Supportive Leadership',
    ],
    Medium: [
      'Competitive Compensation',
      'Good Benefits Package',
      'Talented Colleagues',
      'Interesting Projects',
    ],
    Low: [
      'Decent Benefits',
      'Some Good Teams',
      'Job Stability',
    ],
  };

  const issuesSets = {
    High: [
      'Cross-departmental Communication',
      'Meeting Efficiency',
      'Process Bureaucracy',
    ],
    Medium: [
      'Promotion Transparency',
      'Middle Management Communication',
      'Workload Distribution',
      'Career Path Clarity',
    ],
    Low: [
      'Leadership Communication',
      'Work-Life Balance',
      'Career Development',
      'Employee Recognition',
      'Management Trust',
    ],
  };

  const recommendationsSets = {
    High: [
      {
        priority: 'MEDIUM' as const,
        title: 'Streamline Cross-departmental Communication',
        description:
          'Implement regular inter-departmental meetings and shared communication channels to improve collaboration and reduce silos.',
      },
      {
        priority: 'LOW' as const,
        title: 'Optimize Meeting Culture',
        description:
          'Establish meeting guidelines to reduce unnecessary meetings and improve overall productivity.',
      },
    ],
    Medium: [
      {
        priority: 'HIGH' as const,
        title: 'Improve Leadership Communication',
        description:
          'Conduct monthly one-on-one feedback sessions and establish transparent communication channels between management and employees.',
      },
      {
        priority: 'MEDIUM' as const,
        title: 'Publish Promotion Criteria',
        description:
          'Create and distribute clear promotion guidelines with defined skill requirements and performance metrics.',
      },
      {
        priority: 'MEDIUM' as const,
        title: 'Rebalance Team Workloads',
        description:
          'Conduct workload assessment across teams and redistribute resources to address uneven pressure.',
      },
    ],
    Low: [
      {
        priority: 'HIGH' as const,
        title: 'Urgent Leadership Intervention',
        description:
          'Executive leadership must immediately address communication gaps through town halls, transparent updates, and open feedback channels.',
      },
      {
        priority: 'HIGH' as const,
        title: 'Workload Reform Program',
        description:
          'Implement workload assessment and rebalancing initiative with clear actionable steps to reduce employee burnout.',
      },
      {
        priority: 'HIGH' as const,
        title: 'Establish Career Path Framework',
        description:
          'Create and communicate clear career progression paths with defined milestones and skill development requirements.',
      },
      {
        priority: 'MEDIUM' as const,
        title: 'Employee Recognition Program',
        description:
          'Launch formal recognition program to acknowledge employee contributions and improve morale.',
      },
    ],
  };

  const level = healthScore >= 70 ? 'High' : healthScore >= 50 ? 'Medium' : 'Low';

  return {
    organization_health: healthScore,
    employee_satisfaction: satisfaction,
    executive_summary: executiveSummaries[level],
    strengths: strengthsSets[level],
    critical_issues: issuesSets[level],
    recommendations: recommendationsSets[level],
  };
}

export function generateMockJobs(): AiProcessingJob[] {
  return [
    {
      job_id: 1,
      company_id: 2,
      company_name: 'Google',
      filename: 'employee_feedback_q4_2024.csv',
      records_count: 512,
      status: 'completed',
      progress: 100,
      pipeline_steps: [
        { id: 'upload', name: 'CSV Uploaded', description: '', status: 'completed', progress: 100 },
        { id: 'preprocessing', name: 'Preprocessing', description: '', status: 'completed', progress: 100 },
        { id: 'sentiment', name: 'Sentiment Analysis', description: '', status: 'completed', progress: 100 },
        { id: 'topic', name: 'Topic Modeling', description: '', status: 'completed', progress: 100 },
        { id: 'keyword', name: 'Keyword Extraction', description: '', status: 'completed', progress: 100 },
        { id: 'recommendations', name: 'Recommendation Generation', description: '', status: 'completed', progress: 100 },
        { id: 'completed', name: 'Completed', description: '', status: 'completed', progress: 100 },
      ],
      started_at: '2024-12-10T09:00:00Z',
      completed_at: '2024-12-10T09:45:00Z',
    },
    {
      job_id: 2,
      company_id: 3,
      company_name: 'Microsoft',
      filename: 'annual_survey_results.csv',
      records_count: 1024,
      status: 'processing',
      progress: 65,
      pipeline_steps: [
        { id: 'upload', name: 'CSV Uploaded', description: '', status: 'completed', progress: 100 },
        { id: 'preprocessing', name: 'Preprocessing', description: '', status: 'completed', progress: 100 },
        { id: 'sentiment', name: 'Sentiment Analysis', description: '', status: 'completed', progress: 100 },
        { id: 'topic', name: 'Topic Modeling', description: '', status: 'processing', progress: 60 },
        { id: 'keyword', name: 'Keyword Extraction', description: '', status: 'pending', progress: 0 },
        { id: 'recommendations', name: 'Recommendation Generation', description: '', status: 'pending', progress: 0 },
        { id: 'completed', name: 'Completed', description: '', status: 'pending', progress: 0 },
      ],
      started_at: '2024-12-15T14:30:00Z',
      completed_at: null,
    },
    {
      job_id: 3,
      company_id: 1,
      company_name: 'Amazon',
      filename: 'engagement_survey_q3.csv',
      records_count: 256,
      status: 'queued',
      progress: 0,
      pipeline_steps: [
        { id: 'upload', name: 'CSV Uploaded', description: '', status: 'pending', progress: 0 },
        { id: 'preprocessing', name: 'Preprocessing', description: '', status: 'pending', progress: 0 },
        { id: 'sentiment', name: 'Sentiment Analysis', description: '', status: 'pending', progress: 0 },
        { id: 'topic', name: 'Topic Modeling', description: '', status: 'pending', progress: 0 },
        { id: 'keyword', name: 'Keyword Extraction', description: '', status: 'pending', progress: 0 },
        { id: 'recommendations', name: 'Recommendation Generation', description: '', status: 'pending', progress: 0 },
        { id: 'completed', name: 'Completed', description: '', status: 'pending', progress: 0 },
      ],
      started_at: null,
      completed_at: null,
    },
    {
      job_id: 4,
      company_id: 5,
      company_name: 'Meta',
      filename: 'team_feedback_2024.csv',
      records_count: 128,
      status: 'failed',
      progress: 25,
      pipeline_steps: [
        { id: 'upload', name: 'CSV Uploaded', description: '', status: 'completed', progress: 100 },
        { id: 'preprocessing', name: 'Preprocessing', description: '', status: 'failed', progress: 25, error: 'Invalid data format in column 3' },
        { id: 'sentiment', name: 'Sentiment Analysis', description: '', status: 'pending', progress: 0 },
        { id: 'topic', name: 'Topic Modeling', description: '', status: 'pending', progress: 0 },
        { id: 'keyword', name: 'Keyword Extraction', description: '', status: 'pending', progress: 0 },
        { id: 'recommendations', name: 'Recommendation Generation', description: '', status: 'pending', progress: 0 },
        { id: 'completed', name: 'Completed', description: '', status: 'pending', progress: 0 },
      ],
      started_at: '2024-12-14T11:00:00Z',
      completed_at: null,
      error_message: 'Invalid data format in column 3',
    },
  ];
}

export const mockJobs = generateMockJobs();

export const adminUser = {
  username: 'admin',
  password: 'admin123',
  role: 'admin' as const,
};

export function getCompanyUser(companyId: number) {
  const company = mockCompanies.find((c) => c.company_id === companyId);
  return {
    username: company?.username || 'company',
    password: 'company123',
    role: 'company' as const,
    company: {
      company_id: companyId,
      company_name: company?.company_name || 'Test Company',
    },
  };
}
