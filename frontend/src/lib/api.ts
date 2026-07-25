import type {
  DashboardData,
  Cycle,
  ChartData,
  EntryFormData,
  Profile,
  CycleInsights,
  CycleListResponse,
  CycleDetailComposed,
  CycleDetailResponse,
  InsightsResponse,
  EntryResponse,
  EntryItem,
} from "@/types/fertility";

const INGRESS = (window as any).__INGRESS_PATH__ || "";
const API_BASE = `${INGRESS}/api/v1/fertility`;

export async function fetchDashboard(): Promise<DashboardData> {
  const [insightsRes, cycleRes] = await Promise.all([
    fetch(`${API_BASE}/insights/`),
    fetch(`${API_BASE}/cycles/current`),
  ]);

  if (!insightsRes.ok) throw new Error(`HTTP ${insightsRes.status}`);
  if (!cycleRes.ok) throw new Error(`HTTP ${cycleRes.status}`);

  const insights: InsightsResponse = await insightsRes.json();
  const cycleDetail: CycleDetailResponse = await cycleRes.json();

  let lastTemp: number | null = null;
  if (cycleDetail.temperatures.length > 0) {
    const validTemps = cycleDetail.temperatures
      .filter((t) => !t.is_discarded)
      .sort((a, b) => b.date.localeCompare(a.date));
    if (validTemps.length > 0) {
      lastTemp = validTemps[0].temp_value;
    }
  }

  return {
    cycleId: cycleDetail.id,
    phase: insights.phase as DashboardData["phase"],
    cycle_day: insights.cycle_day,
    avg_cycle_length: insights.avg_cycle_length,
    next_period_date: insights.next_period_date,
    fertile_start_date: insights.fertile_start,
    fertile_end_date: insights.fertile_end,
    ovulation_date: insights.ovulation_date,
    ovulation_confirmed: insights.ovulation_confirmed,
    coverline: insights.coverline,
    last_temp: lastTemp,
    luteal_length: insights.luteal_length,
    warnings: insights.warnings,
  };
}

export async function fetchCycles(): Promise<Cycle[]> {
  const res = await fetch(`${API_BASE}/cycles/`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data: CycleListResponse = await res.json();
  return data.cycles;
}

export async function fetchCycleDetail(
  cycleId: string
): Promise<CycleDetailComposed> {
  const res = await fetch(`${API_BASE}/cycles/${cycleId}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const detail: CycleDetailResponse = await res.json();

  const cycle: Cycle = {
    id: detail.id,
    start_date: detail.start_date,
    end_date: detail.end_date,
    cycle_length: detail.cycle_length,
    ovulation_date: detail.insights?.ovulation_date ?? null,
    ovulation_confirmed: detail.insights?.ovulation_confirmed ?? false,
    luteal_length: detail.insights?.luteal_length ?? null,
    is_active: detail.end_date === null,
  };

  const insights: CycleInsights = detail.insights
    ? {
        coverline: detail.insights.coverline,
        ovulation_date: detail.insights.ovulation_date,
        ovulation_confirmed: detail.insights.ovulation_confirmed,
        fertile_start_date: detail.insights.fertile_start_date,
        fertile_end_date: detail.insights.fertile_end_date,
        luteal_length: detail.insights.luteal_length,
        luteal_phase_short: detail.insights.luteal_phase_short,
        pregnancy_indicator: detail.insights.pregnancy_indicator,
        consecutive_elevated_temps: detail.insights.consecutive_elevated_temps,
      }
    : {
        coverline: null,
        ovulation_date: null,
        ovulation_confirmed: false,
        fertile_start_date: null,
        fertile_end_date: null,
        luteal_length: null,
        luteal_phase_short: false,
        pregnancy_indicator: false,
        consecutive_elevated_temps: 0,
      };

  const dateMap = new Map<string, EntryItem>();

  for (const t of detail.temperatures) {
    if (!dateMap.has(t.date)) {
      dateMap.set(t.date, {
        day: 0,
        date: t.date,
        temp: null,
        flow: "",
        mucus: "",
        opk: "",
        symptoms: [],
      });
    }
    if (!t.is_discarded) {
      dateMap.get(t.date)!.temp = t.temp_value;
    }
  }

  for (const s of detail.signs) {
    if (!dateMap.has(s.date)) {
      dateMap.set(s.date, {
        day: 0,
        date: s.date,
        temp: null,
        flow: "",
        mucus: "",
        opk: "",
        symptoms: [],
      });
    }
    const entry = dateMap.get(s.date)!;
    entry.flow = s.menstrual_flow;
    entry.mucus = s.cervical_mucus;
    entry.opk = s.opk_result;
  }

  for (const s of detail.symptoms) {
    if (!dateMap.has(s.date)) {
      dateMap.set(s.date, {
        day: 0,
        date: s.date,
        temp: null,
        flow: "",
        mucus: "",
        opk: "",
        symptoms: [],
      });
    }
    dateMap.get(s.date)!.symptoms.push(s.symptom_type);
  }

  const entries: EntryItem[] = Array.from(dateMap.values())
    .sort((a, b) => a.date.localeCompare(b.date))
    .map((e, i) => ({ ...e, day: i + 1 }));

  return { cycle, insights, entries };
}

export async function fetchChartData(cycleId: string): Promise<ChartData> {
  const res = await fetch(`${API_BASE}/cycles/${cycleId}/chart`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function createEntry(data: EntryFormData): Promise<EntryResponse> {
  const body: Record<string, unknown> = {
    date: data.date,
    time_taken: data.time_taken || null,
    is_discarded: data.is_discarded,
    discard_reason: data.discard_reason,
    menstrual_flow: data.menstrual_flow,
    cervical_mucus: data.cervical_mucus,
    cervical_position: data.cervical_position,
    cervical_firmness: data.cervical_firmness,
    cervical_opening: data.cervical_opening,
    opk_result: data.opk_result,
    symptoms: data.symptoms,
    symptom_severity: data.symptom_severity,
    is_period_start: data.is_period_start,
    notes: data.notes,
  };

  if (data.temp_value !== "" && !isNaN(Number(data.temp_value))) {
    body.temp_value = Number(data.temp_value);
  }

  const res = await fetch(`${API_BASE}/entries/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchTodayEntry(): Promise<EntryResponse | null> {
  const res = await fetch(`${API_BASE}/entries/today`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function fetchProfiles(): Promise<Profile[]> {
  const res = await fetch(`${API_BASE}/profiles/`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function createProfile(data: {
  name: string;
  temp_unit?: string;
}): Promise<Profile> {
  const res = await fetch(`${API_BASE}/profiles/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function deleteProfile(profileId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/profiles/${profileId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
}

export async function activateProfile(profileId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/profiles/${profileId}/activate`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
}

export async function exportData(): Promise<Blob> {
  const profiles: Profile[] = await fetchProfiles();
  const activeProfile = profiles.find((p) => p.is_active);
  if (!activeProfile) throw new Error("No active profile found");

  const res = await fetch(
    `${API_BASE}/profiles/${activeProfile.id}/export`
  );
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const json = await res.json();
  return new Blob([JSON.stringify(json, null, 2)], {
    type: "application/json",
  });
}

export async function reanalyzeInsights(): Promise<InsightsResponse> {
  const res = await fetch(`${API_BASE}/insights/reanalyze`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function createCycle(): Promise<CycleDetailResponse> {
  const res = await fetch(`${API_BASE}/cycles/`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
