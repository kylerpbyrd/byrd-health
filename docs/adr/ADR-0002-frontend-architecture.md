# ADR-0002: Frontend Architecture

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | Web frontend application                       |

---

## 1. Context

Byrd Health requires a user interface for fertility data entry, chart visualization, cycle history, and profile management. The frontend must:

- Be portable between Home Assistant (Phase 3) and ByrdOS (future)
- Support mobile-first workflows (daily temperature logging on phone)
- Render BBT charts with annotations (coverline, fertile window, ovulation)
- Be accessible (WCAG 2.1 AA target)
- Be independently testable from the backend

The legacy application uses server-rendered Jinja2 templates with Chart.js — a pattern that does not meet portability requirements.

## 2. Decision

Use **React 18+ with TypeScript** as the primary frontend framework, with:

- **Vite** for build tooling
- **Tailwind CSS** for styling
- **shadcn/ui** for component primitives
- **Recharts** for charting
- **TanStack Query** (React Query) for server state management
- **React Router** for client-side routing

### 2.1 Why React over Lit or other alternatives

| Alternative     | Why Rejected                                        |
|-----------------|-----------------------------------------------------|
| Lit (Web Components) | Better for HA Lovelace cards, but limited ecosystem for complex data-entry SPAs |
| Svelte          | Smaller ecosystem, fewer shadcn/ui-quality libraries |
| Vue             | Good but React has broader TypeScript + ecosystem support |
| HTMX + templates| Not portable, server-rendered, no offline support    |

### 2.2 Why Recharts over Chart.js

| Factor          | Recharts                           | Chart.js                         |
|-----------------|------------------------------------|----------------------------------|
| React-native    | Yes (declarative JSX)              | Wrapper required                 |
| TypeScript      | First-class                        | Requires @types                  |
| Customization   | Composable components              | Plugin-based                     |
| BBT suitability | Line chart + reference lines       | Excellent (legacy uses it)       |

Recharts provides sufficient BBT charting capabilities. Custom annotations (coverline, fertile window box, ovulation line) can be built using `ReferenceLine` and `ReferenceArea` components. If Recharts proves insufficient for advanced annotations, Chart.js remains a viable fallback.

### 2.3 Component Architecture

```
src/
├── App.tsx                    # Root with router
├── pages/
│   ├── DashboardPage.tsx      # Phase banner + stats + mini chart
│   ├── EntryPage.tsx          # Daily temperature/signs form
│   ├── HistoryPage.tsx        # Cycle list table
│   ├── CycleDetailPage.tsx    # Full chart + daily log
│   ├── ProfilesPage.tsx       # Profile CRUD
│   └── SettingsPage.tsx       # Profile settings
├── components/
│   ├── ui/                    # shadcn/ui primitives
│   ├── BBTChart.tsx           # BBT chart with annotations
│   ├── PhaseBanner.tsx        # Cycle phase indicator
│   ├── StatTile.tsx           # Metric display
│   ├── EntryForm.tsx          # Temperature + signs form
│   ├── SymptomSelector.tsx    # Symptom checkboxes
│   ├── FertilitySignsForm.tsx # Signs radio groups
│   ├── CycleTable.tsx         # History table
│   └── WarningBanner.tsx      # Alerts display
├── hooks/
│   ├── useDashboard.ts        # Dashboard data query
│   ├── useCycle.ts            # Cycle data query
│   ├── useProfile.ts          # Profile query/mutation
│   └── useWebSocket.ts        # Real-time (future)
├── lib/
│   ├── api.ts                 # API client
│   ├── query-client.ts        # TanStack Query config
│   └── utils.ts               # Formatters
└── types/
    └── fertility.ts           # TypeScript interfaces
```

## 3. Consequences

### Positive
- React SPA is fully portable between HA Ingress and ByrdOS
- Recharts provides declarative, composable chart components
- shadcn/ui gives accessible, customizable UI primitives
- TanStack Query handles caching, refetching, optimistic updates

### Negative
- Larger initial bundle vs. server-rendered templates
- Learning curve for shadcn/ui component model
- Recharts may need workarounds for BBT-specific annotations (coverline, fertile box)

### Risks
- Recharts annotation capabilities may be insufficient (fallback: Chart.js via react-chartjs-2)
- Mobile form UX may require additional iteration beyond shadcn/ui defaults

## 4. Home Assistant Lovelace Card (Phase 3)

The Lovelace card is a **separate component** using Lit + TypeScript. It does not share code with the React SPA. This is deliberate: the card is an HA integration, not a platform component.

## 5. References

- `docs/ARCHITECTURE_RECOMMENDATIONS.md §4` — Frontend recommendations
- `docs/LEGACY_REVIEW.md §8.10` — Chart.js implementation analysis
- `ADR-0001` — Platform architecture
