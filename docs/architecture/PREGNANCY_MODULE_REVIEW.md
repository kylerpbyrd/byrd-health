# Pregnancy Module Review

> **Date:** 2026-07-26 | **Reviewer:** Architect  
> **Module:** `pregnancy_engine` + pregnancy domain across stack

---

## Architecture Assessment: PASS

The pregnancy module correctly follows the modular monolith pattern established by the fertility module. It is a **well-structured domain extension** that does not compromise the architecture.

### Layer-by-Layer Assessment

| Layer | Package | Assessment |
|---|---|---|
| **Engine** | `pregnancy_engine` | Pure Python. Zero framework dependencies. 4 public functions: `calculate_due_date`, `calculate_current_week`, `calculate_trimester`, `calculate_days_remaining`. Identical isolation pattern to `fertility_engine`. |
| **Data** | `data_service` | `Pregnancy` SQLAlchemy model follows all existing conventions (UUID PK, FK with CASCADE, timestamps, relationships). Migration is additive. Repository follows the established pattern. |
| **API** | `web_api/routers/pregnancy.py` | 3 endpoints (POST, GET, PATCH). Uses standard dependencies (`get_active_profile`, `get_data_service`). Follows REST conventions. Minor: missing OpenAPI `responses` dicts. |
| **Frontend** | `PregnancyPage.tsx` | Functional dashboard with 3 states. Uses existing UI components. Route registered via lazy loading. Minor: uses raw fetch instead of React Query. |

---

## Domain Model Review

### Correctness

| Concept | Implementation | Verdict |
|---|---|---|
| Due date from ovulation | `ovulation_date + 266 days` | ✅ Correct (Naegele's rule, ovulation method) |
| Due date from LMP | `lmp_date + 280 days` | ✅ Correct (Naegele's rule, standard method) |
| Current week | `(today - LMP) / 7 + 1` | ✅ Correct (week 1 starts at LMP) |
| Trimester boundaries | 1: 1-13, 2: 14-26, 3: 27+ | ✅ Correct (ACOG standard) |
| One pregnancy per cycle | `cycle_id` unique constraint | ✅ Correct (a pregnancy originates from a specific cycle) |

### Edge Cases Handled

| Case | Behavior | Verdict |
|---|---|---|
| No ovulation or LMP provided | Returns `None` | ✅ Graceful |
| Ovulation provided (preferred) | Uses ovulation method, ignores LMP | ✅ Correct (ovulation method is more accurate) |
| Reference date in the past | Week and days_remaining reflect past date | ✅ Correct (useful for retrospective queries) |
| Week 0 or negative | `max(1, calculated_week)` | ✅ Guards against edge cases |
| Due date in the past | `max(0, days_remaining)` | ✅ Guards against negative days |

---

## Separation from Fertility Engine

The pregnancy module is correctly separated from the fertility engine:

- **Zero imports** from `fertility_engine` in `pregnancy_engine`
- **No shared state** between the two modules
- **Interaction through data_service** — pregnancy reads cycle data via the repository layer, not by importing fertility logic
- **Independent testability** — pregnancy_engine tests run without fertility_engine (confirmed: 7 tests pass independently)

This separation is important because pregnancy tracking is a **different clinical domain** than fertility tracking. A user might:
- Track fertility without becoming pregnant (most users)
- Track pregnancy without prior fertility tracking (new users starting at pregnancy)
- Track both sequentially (fertility → pregnancy)

The current architecture supports all three scenarios.

---

## Frontend Pattern Divergence

### Concern: Raw fetch vs. React Query

`PregnancyPage` uses:
```typescript
useEffect(() => { fetchPregnancy().then(setPregnancy) }, [])
useEffect(() => { fetchCycles().then(setCycles) }, [])
```

All other pages use `@tanstack/react-query`:
```typescript
const { data } = useDashboard()  // React Query hook
```

**Impact:** Cache inconsistency. A pregnancy started on the PregnancyPage will not automatically invalidate dashboard data or appear in other contexts. React Query provides automatic cache invalidation, stale revalidation, and retry logic — all missing from the raw fetch approach.

**Recommendation:** Create a `usePregnancy` hook:
```typescript
// frontend/src/hooks/usePregnancy.ts
export function usePregnancy() {
  return useQuery({
    queryKey: ["pregnancy"],
    queryFn: fetchPregnancy,
  });
}

export function useStartPregnancy() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: startPregnancy,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["pregnancy"] }),
  });
}
```

This provides:
- Automatic loading/error states
- Cache invalidation on mutation success
- Stale-time management
- Retry on network failure
- Consistent pattern with all other pages

---

## Recommendations

### Before Next Module (Phase 4B)

1. **Refactor PregnancyPage to React Query** — This establishes the correct pattern for all future frontend pages. Do not ship the raw-fetch pattern to Phase 4B.

2. **Remove unused `pydantic>=2.0` dependency** from `pregnancy_engine/pyproject.toml`. The engine is pure Python with zero Pydantic usage. Clean dependency declarations are essential for the modular monolith to scale.

3. **Document the module pattern** in `FUTURE_MODULE_STRATEGY.md` — add a "Phase 4A Postmortem" section noting lessons learned: React Query is mandatory, routers must have OpenAPI responses dicts, Graphify edges must be verified before commit.

### For Phase 4C (Sleep)

4. **Follow the same package structure** — `sleep_engine/` + data model extension + REST router + frontend page.

### For Phase 5 (Wearables)

5. **Pregnancy data from wearables** — Apple Health and Fitbit provide pregnancy-related data (weight, heart rate, resting heart rate). The `device_adapters` pattern supports adding pregnancy-specific adapters that write to the `Pregnancy` model.

---

## Conclusion

The pregnancy module is **architecturally sound** and follows the established modular monolith pattern. The engine, data model, API, and frontend are correctly separated. Two issues (React Query pattern, extraneous dependency) should be resolved before Phase 4B to prevent pattern drift from becoming technical debt.
