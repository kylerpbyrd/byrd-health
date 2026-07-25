import type {
  DashboardData,
  Cycle,
  ChartData,
  Profile,
  CycleInsights,
} from "@/types/fertility";

export const mockProfiles: Profile[] = [
  {
    id: "profile-1",
    name: "Default Profile",
    slug: "default",
    temp_unit: "F",
    interpretation_method: "standard",
    is_active: true,
    created_at: "2026-01-01T00:00:00Z",
  },
  {
    id: "profile-2",
    name: "Partner Profile",
    slug: "partner",
    temp_unit: "C",
    interpretation_method: "conservative",
    is_active: false,
    created_at: "2026-06-01T00:00:00Z",
  },
];

export const mockDashboardData: DashboardData = {
  cycleId: "cycle-3",
  phase: "luteal",
  cycle_day: 18,
  avg_cycle_length: 28,
  next_period_date: "2026-07-28",
  fertile_start_date: "2026-07-07",
  fertile_end_date: "2026-07-11",
  ovulation_date: "2026-07-09",
  ovulation_confirmed: true,
  coverline: 97.52,
  last_temp: 98.15,
  luteal_length: null,
  warnings: [
    {
      type: "info",
      message:
        "3rd cycle — data may be limited. Predictions improve with more cycles logged.",
    },
  ],
};

export const mockCycles: Cycle[] = [
  {
    id: "cycle-3",
    start_date: "2026-07-06",
    end_date: null,
    cycle_length: null,
    ovulation_date: "2026-07-09",
    ovulation_confirmed: true,
    luteal_length: null,
    is_active: true,
  },
  {
    id: "cycle-2",
    start_date: "2026-06-07",
    end_date: "2026-07-05",
    cycle_length: 29,
    ovulation_date: "2026-06-21",
    ovulation_confirmed: true,
    luteal_length: 14,
    is_active: false,
  },
  {
    id: "cycle-1",
    start_date: "2026-05-08",
    end_date: "2026-06-06",
    cycle_length: 30,
    ovulation_date: "2026-05-22",
    ovulation_confirmed: true,
    luteal_length: 15,
    is_active: false,
  },
];

function generateTemperatures(): (number | null)[] {
  const temps: (number | null)[] = [
    97.62, 97.55, 97.48, 97.58, 97.45, 97.52, 97.41, 97.38, 97.49, 97.35,
    97.33, 97.42, 97.56, 97.61, 97.78, 97.82, 97.95, 98.02, 98.15,
  ];
  return temps;
}

function generateDiscarded(): Array<{ x: string; y: number }> {
  return [{ x: "07-10", y: 98.21 }];
}

function generateMucus(): Record<string, string> {
  return {
    "07-06": "sticky",
    "07-07": "sticky",
    "07-08": "creamy",
    "07-09": "watery",
    "07-10": "egg_white",
    "07-11": "watery",
    "07-12": "creamy",
    "07-13": "dry",
    "07-14": "dry",
    "07-15": "dry",
    "07-16": "dry",
    "07-17": "dry",
    "07-18": "dry",
  };
}

function generateOPK(): Record<string, string> {
  return {
    "07-07": "low",
    "07-08": "high",
    "07-09": "peak",
    "07-10": "high",
    "07-11": "low",
  };
}

export const mockChartData: ChartData = {
  labels: [
    "07-06", "07-07", "07-08", "07-09", "07-10", "07-11", "07-12",
    "07-13", "07-14", "07-15", "07-16", "07-17", "07-18", "07-19",
    "07-20", "07-21", "07-22", "07-23", "07-24",
  ],
  temperatures: generateTemperatures(),
  discarded: generateDiscarded(),
  coverline: 97.52,
  fertile_start_day: 3,
  fertile_end_day: 6,
  ovulation_day: 5,
  mucus: generateMucus(),
  opk: generateOPK(),
  unit: "F",
};

export const mockCycleDetail: {
  cycle: Cycle;
  insights: CycleInsights;
  entries: Array<Record<string, unknown>>;
} = {
  cycle: mockCycles[0],
  insights: {
    coverline: 97.52,
    ovulation_date: "2026-07-09",
    ovulation_confirmed: true,
    fertile_start_date: "2026-07-07",
    fertile_end_date: "2026-07-11",
    luteal_length: null,
    luteal_phase_short: false,
    pregnancy_indicator: false,
    consecutive_elevated_temps: 4,
  },
  entries: [
    {
      day: 1,
      date: "2026-07-06",
      temp: 97.62,
      flow: "medium",
      mucus: "sticky",
      opk: "not_tested",
      symptoms: ["cramps"],
    },
    {
      day: 2,
      date: "2026-07-07",
      temp: 97.55,
      flow: "light",
      mucus: "sticky",
      opk: "low",
      symptoms: [],
    },
    {
      day: 3,
      date: "2026-07-08",
      temp: 97.48,
      flow: "none",
      mucus: "creamy",
      opk: "high",
      symptoms: [],
    },
    {
      day: 4,
      date: "2026-07-09",
      temp: 97.38,
      flow: "none",
      mucus: "watery",
      opk: "peak",
      symptoms: ["ovulation_pain"],
    },
    {
      day: 5,
      date: "2026-07-10",
      temp: 98.21,
      flow: "none",
      mucus: "egg_white",
      opk: "high",
      symptoms: [],
    },
    {
      day: 6,
      date: "2026-07-11",
      temp: 97.35,
      flow: "none",
      mucus: "watery",
      opk: "low",
      symptoms: [],
    },
    {
      day: 7,
      date: "2026-07-12",
      temp: 97.33,
      flow: "none",
      mucus: "creamy",
      opk: "not_tested",
      symptoms: [],
    },
    {
      day: 8,
      date: "2026-07-13",
      temp: 97.42,
      flow: "none",
      mucus: "dry",
      opk: "not_tested",
      symptoms: ["fatigue"],
    },
    {
      day: 9,
      date: "2026-07-14",
      temp: 97.56,
      flow: "none",
      mucus: "dry",
      opk: "not_tested",
      symptoms: [],
    },
    {
      day: 10,
      date: "2026-07-15",
      temp: 97.61,
      flow: "none",
      mucus: "dry",
      opk: "not_tested",
      symptoms: [],
    },
    {
      day: 11,
      date: "2026-07-16",
      temp: 97.78,
      flow: "none",
      mucus: "dry",
      opk: "not_tested",
      symptoms: [],
    },
    {
      day: 12,
      date: "2026-07-17",
      temp: 97.82,
      flow: "none",
      mucus: "dry",
      opk: "not_tested",
      symptoms: ["bloating"],
    },
    {
      day: 13,
      date: "2026-07-18",
      temp: 98.02,
      flow: "none",
      mucus: "dry",
      opk: "not_tested",
      symptoms: [],
    },
    {
      day: 14,
      date: "2026-07-19",
      temp: 98.15,
      flow: "none",
      mucus: "dry",
      opk: "not_tested",
      symptoms: [],
    },
  ],
};
