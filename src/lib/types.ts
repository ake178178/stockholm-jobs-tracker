export interface Job {
  id: string;
  title: string;
  company: string;
  company_key: string;
  location: string;
  url: string;
  posted: string;
  job_type: string;
  match_score: number;
  match_reasons: string[];
  team: string;
  is_new: boolean;
}

export interface DailyData {
  date: string;
  generated_at: string;
  jobs: Job[];
  stats: {
    total: number;
    new_count: number;
    by_company: Record<string, number>;
  };
}
