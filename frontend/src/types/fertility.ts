export type TempUnit = "F" | "C";
export type InterpretationMethod = "standard" | "conservative";
export type CyclePhase =
  | "menstruation"
  | "pre_ovulatory"
  | "fertile"
  | "ovulation"
  | "luteal"
  | "unknown";

export interface Profile {
  id: string;
  name: string;
  slug: string;
  temp_unit: TempUnit;
  interpretation_method: InterpretationMethod;
  is_active: boolean;
  created_at: string;
}

export interface InsightsDataResponse {
  id: string;
  cycle_id: string;
  coverline: number | null;
  ovulation_date: string | null;
  ovulation_confirmed: boolean;
  ovulation_confidence: string;
  ovulation_method: string;
  fertile_start_date: string | null;
  fertile_end_date: string | null;
  post_ovulatory_infertile_date: string | null;
  luteal_length: number | null;
  luteal_phase_short: boolean;
  pregnancy_indicator: boolean;
  consecutive_elevated_temps: number;
  engine_version: string;
  computed_at: string | null;
}

export interface CycleInsights {
  coverline: number | null;
  ovulation_date: string | null;
  ovulation_confirmed: boolean;
  fertile_start_date: string | null;
  fertile_end_date: string | null;
  luteal_length: number | null;
  luteal_phase_short: boolean;
  pregnancy_indicator: boolean;
  consecutive_elevated_temps: number;
}

export interface InsightsResponse {
  cycle_day: number;
  phase: string;
  coverline: number | null;
  ovulation_date: string | null;
  ovulation_confirmed: boolean;
  ovulation_confidence: string;
  ovulation_method: string;
  fertile_start: string | null;
  fertile_end: string | null;
  luteal_length: number | null;
  luteal_phase_short: boolean;
  pregnancy_indicator: boolean;
  next_period_date: string | null;
  avg_cycle_length: number | null;
  warnings: Array<{ type: string; message: string }>;
  engine_version: string;
}

export interface DashboardData {
  cycleId: string;
  phase: CyclePhase;
  cycle_day: number;
  avg_cycle_length: number | null;
  next_period_date: string | null;
  fertile_start_date: string | null;
  fertile_end_date: string | null;
  ovulation_date: string | null;
  ovulation_confirmed: boolean;
  coverline: number | null;
  last_temp: number | null;
  luteal_length: number | null;
  warnings: Array<{ type: string; message: string }>;
}

export interface Cycle {
  id: string;
  start_date: string;
  end_date: string | null;
  cycle_length: number | null;
  ovulation_date: string | null;
  ovulation_confirmed: boolean;
  luteal_length: number | null;
  is_active: boolean;
}

export interface CycleListResponse {
  cycles: Cycle[];
}

export interface TempEntry {
  id: string;
  cycle_id: string;
  date: string;
  temp_value: number;
  time_taken: string | null;
  is_discarded: boolean;
  discard_reason: string;
  notes: string;
}

export interface SignsEntry {
  id: string;
  cycle_id: string;
  date: string;
  menstrual_flow: string;
  cervical_mucus: string;
  cervical_position: string;
  cervical_firmness: string;
  cervical_opening: string;
  opk_result: string;
  notes: string;
}

export interface SymptomEntry {
  id: string;
  cycle_id: string;
  date: string;
  symptom_type: string;
  severity: number;
}

export interface EntryResponse {
  temperature: TempEntry | null;
  signs: SignsEntry | null;
  symptoms: SymptomEntry[];
}

export interface CycleDetailResponse {
  id: string;
  profile_id: string;
  start_date: string;
  end_date: string | null;
  cycle_length: number | null;
  notes: string;
  temperatures: TempEntry[];
  signs: SignsEntry[];
  symptoms: SymptomEntry[];
  insights: InsightsDataResponse | null;
}

export interface CycleDetailComposed {
  cycle: Cycle;
  insights: CycleInsights;
  entries: EntryItem[];
}

export interface EntryItem {
  day: number;
  date: string;
  temp: number | null;
  flow: string;
  mucus: string;
  opk: string;
  symptoms: string[];
}

export interface ChartData {
  labels: string[];
  temperatures: (number | null)[];
  discarded: Array<{ x: string; y: number }>;
  coverline: number | null;
  fertile_start_day: number | null;
  fertile_end_day: number | null;
  ovulation_day: number | null;
  mucus: Record<string, string>;
  opk: Record<string, string>;
  unit: TempUnit;
}

export interface EntryFormData {
  date: string;
  temp_value: string;
  time_taken: string;
  is_discarded: boolean;
  discard_reason: string;
  menstrual_flow: string;
  cervical_mucus: string;
  cervical_position: string;
  cervical_firmness: string;
  cervical_opening: string;
  opk_result: string;
  symptoms: string[];
  symptom_severity: number;
  is_period_start: boolean;
  notes: string;
}

export interface ExportResponse {
  format: string;
  version: number;
  exported_at: string;
  profile: Profile;
  cycles: CycleExportItem[];
}

export interface CycleExportItem {
  id: string;
  start_date: string;
  end_date: string | null;
  cycle_length: number | null;
  notes: string;
  temperatures: TempEntry[];
  fertility_signs: SignsEntry[];
  symptoms: SymptomEntry[];
  insights: InsightsDataResponse | null;
}

export interface CalendarDay {
  date: string;
  cycle_day: number | null;
  phase: string | null;
  temp: number | null;
  flow: string | null;
  mucus: string | null;
  opk: string | null;
  is_period_start: boolean;
  is_ovulation_day: boolean;
  is_fertile: boolean;
  is_today: boolean;
  has_entry: boolean;
  in_current_month: boolean;
}

export interface CalendarCycleInRange {
  id: string;
  start_date: string;
  end_date: string | null;
  phase_dates: Record<string, string[]>;
}

export interface CalendarResponse {
  month: string;
  profile: {
    slug: string;
    temp_unit: string;
  };
  days: CalendarDay[];
  cycles_in_range: CalendarCycleInRange[];
}
