export type PriorityLevel = 'HIGH' | 'MEDIUM' | 'LOW';
export type SatisfactionLevel = 'High' | 'Medium' | 'Low';

export interface Recommendation {
  priority: PriorityLevel;
  title: string;
  description: string;
}

export interface DecisionSupportData {
  organization_health: number;
  employee_satisfaction: SatisfactionLevel;
  executive_summary: string;
  strengths: string[];
  critical_issues: string[];
  recommendations: Recommendation[];
}

export interface HealthScoreCategory {
  label: string;
  min: number;
  max: number;
  color: string;
}

export const HealthScoreCategories: HealthScoreCategory[] = [
  { label: 'Critical', min: 0, max: 40, color: '#EF4444' },
  { label: 'Needs Improvement', min: 41, max: 60, color: '#F59E0B' },
  { label: 'Good', min: 61, max: 80, color: '#10B981' },
  { label: 'Excellent', min: 81, max: 100, color: '#2563EB' },
];

export function getHealthCategory(score: number): HealthScoreCategory {
  return HealthScoreCategories.find(
    (cat) => score >= cat.min && score <= cat.max
  ) || HealthScoreCategories[0];
}
