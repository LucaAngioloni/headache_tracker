export type Medicine = {
  id: number;
  name: string;
  active_ingredient: string;
  unit: string;
};

export type Trigger = {
  id: number;
  name: string;
};

export type Dose = {
  id?: number;
  medicine: number;
  medicine_name?: string;
  medicine_unit?: string;
  quantity: string | number;
  note: string;
  sort_order?: number;
};

export type Episode = {
  id: number;
  occurred_on: string;
  pain_level: number | null;
  notes: string;
  trigger_ids: number[];
  triggers: Trigger[];
  doses: Dose[];
  created_at: string;
  updated_at: string;
};

export type EpisodeWrite = {
  occurred_on: string;
  pain_level: number | null;
  notes: string;
  trigger_ids: number[];
  doses: Array<{
    medicine: number;
    quantity: string | number;
    note: string;
    sort_order?: number;
  }>;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type Me = {
  id: number;
  username: string;
};

export type EpisodeFilters = {
  date_after?: string;
  date_before?: string;
  medicine?: number | "";
  trigger?: number | "";
  pain_min?: number | "";
  pain_max?: number | "";
  search?: string;
};

export type Stats = {
  filters: Record<string, string | null>;
  episode_count: number;
  avg_pain: number | null;
  median_pain: number | null;
  avg_days_between: number | null;
  current_headache_free_streak_days: number;
  longest_headache_free_streak_days: number;
  second_dose_rate: number;
  episodes_by_month: Array<{ month: string; count: number }>;
  episodes_by_week: Array<{ week: string; count: number }>;
  medicines: Array<{
    id: number;
    name: string;
    dose_count: number;
    episode_count: number;
    pct: number;
  }>;
  triggers: Array<{
    id: number;
    name: string;
    episode_count: number;
    pct: number;
  }>;
};
