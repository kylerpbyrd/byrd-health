# ADR-0010: Graphify Knowledge Architecture

| Key          | Value                                          |
|--------------|------------------------------------------------|
| **Status**   | Accepted                                       |
| **Date**     | 2026-07-23                                     |
| **Deciders** | Lead Architect, User                           |
| **Replaces** | None                                           |
| **Scope**    | Project knowledge management                   |

---

## 1. Context

Graphify is the canonical knowledge layer for the Byrd Health project. It serves as:

- A graph-based index of all project entities, services, ADRs, and relationships
- The first query point before any agent begins work
- The last update point after any agent completes work
- The source of truth for dependency tracking and deduplication

The legacy project maintained Graphify as a concept without implementation. The `graph/` directory exists but is empty. Phase 0 produced a comprehensive indexing plan (`docs/GRAPHIFY_INDEX_PLAN.md`).

## 2. Decision

Graphify is implemented as a **filesystem-based knowledge graph** using a simple, agent-accessible format. The Knowledge Engineer agent owns Graphify integrity.

### 2.1 Graph Structure

```
graph/
├── nodes/                   # One JSON file per node
│   ├── services/
│   │   ├── fertility-engine.json
│   │   ├── data-service.json
│   │   ├── web-api.json
│   │   ├── web-frontend.json
│   │   ├── ha-bridge.json
│   │   └── device-adapters.json
│   ├── entities/
│   │   ├── profile.json
│   │   ├── cycle.json
│   │   ├── temperature-record.json
│   │   └── ...
│   ├── agents/
│   │   ├── architect.json
│   │   ├── backend-engineer.json
│   │   └── ...
│   ├── adrs/
│   │   ├── adr-0001.json
│   │   └── ...
│   ├── apis/
│   │   ├── fertility-api-v1.json
│   │   └── ...
│   ├── documents/
│   │   ├── legacy-review.json
│   │   └── ...
│   ├── concepts/
│   │   ├── privacy-first.json
│   │   └── ...
│   ├── integrations/
│   │   ├── home-assistant.json
│   │   └── ...
│   └── milestones/
│       ├── phase-0.json
│       └── ...
├── edges.json               # All relationships
└── index.json               # Node registry with metadata
```

### 2.2 Node Format

```json
{
  "id": "entity:profile",
  "type": "entity",
  "label": "Profile",
  "description": "User profile with fertility tracking settings",
  "source": "ADR-0004",
  "properties": {
    "table": "profiles",
    "primary_key": "id (UUID)",
    "fields": ["name", "slug", "temp_unit", "interpretation_method"]
  },
  "created_at": "2026-07-23T00:00:00Z",
  "updated_at": "2026-07-23T00:00:00Z"
}
```

### 2.3 Edge Format

```json
{
  "edges": [
    {
      "source": "service:web-api",
      "target": "service:data-service",
      "relationship": "DEPENDS_ON",
      "description": "Web API requires Data Service for all persistence operations"
    },
    {
      "source": "service:fertility-engine",
      "target": "entity:temperature-record",
      "relationship": "CONSUMES",
      "description": "Fertility Engine reads temperature records as input"
    }
  ]
}
```

### 2.4 Relationship Types

| Relationship     | Meaning                             | Example                          |
|------------------|-------------------------------------|----------------------------------|
| `DEPENDS_ON`     | A requires B to function            | web-api → data-service           |
| `IMPLEMENTS`     | A implements B's interface          | ha-bridge → HABridgeProtocol     |
| `PRODUCES`       | A generates B                       | fertility-engine → CycleInsights |
| `CONSUMES`       | A reads/uses B                      | web-frontend → web-api           |
| `OWNS`           | A has authority over B              | architect → all agents           |
| `REFERENCES`     | A documents or refers to B          | adr-0003 → legacy-review         |
| `PRECEDES`       | A must happen before B              | phase-1 → phase-2                |
| `VERSION_OF`     | A is a new version of B             | fertility-engine → legacy-algorithms |
| `ISOLATES`       | A encapsulates B-specific logic     | ha-bridge → home-assistant       |
| `INTEGRATES_WITH`| A connects to external system       | ha-bridge → home-assistant       |

### 2.5 Agent Workflow with Graphify

```
Before work:
  1. Query Graphify for existing nodes related to task
  2. Check for duplicate implementations
  3. Identify related ADRs
  4. Note dependencies

After work:
  1. Create/update nodes for any new entities, services, or modules
  2. Add relationships (DEPENDS_ON, PRODUCES, CONSUMES, etc.)
  3. Update index.json with timestamps
  4. Verify no orphan nodes
```

### 2.6 Graphify Health Checks

The Knowledge Engineer periodically verifies:

- [ ] Every service has a relationship to at least one module
- [ ] Every entity is PRODUCED or CONSUMED by at least one service
- [ ] Every ADR REFERENCES at least one service or concept
- [ ] Every document is REFERENCED by at least one node
- [ ] No orphan nodes exist (zero relationships)
- [ ] No circular DEPENDS_ON relationships
- [ ] Legacy components have VERSION_OF links to new components
- [ ] Agent OWNERSHIP covers every service

## 3. Consequences

### Positive
- Filesystem-based format is agent-accessible (no database dependency)
- JSON is easily read, written, and validated
- Clear relationship types enable dependency analysis
- Index provides fast lookup without loading all nodes

### Negative
- Manual updates required (no auto-detection of code changes)
- Risk of stale state if agents forget to update
- No built-in query language (search is file-based)

### Risks
- Stale Graphify state — mitigated by the "stale state is a defect" rule and periodic health checks
- Inconsistent node IDs — mitigated by the naming convention (`type:name`)
- Missing relationships — mitigated by the health check list

## 4. Phase 1 Indexing Scope

The Knowledge Engineer must index all Phase 0 deliverables:

1. All entities from `docs/GRAPHIFY_INDEX_PLAN.md §2`
2. All services from `§3`
3. All agents from `§4`
4. All documents from `§5`
5. All ADRs from `§6`
6. All API groups from `§7`
7. All integrations from `§8`
8. Legacy-to-new mappings from `§9`
9. All concepts from `§10`
10. All milestones from `§11`

Plus all 10 ADR documents created in Phase 1.

## 5. References

- `docs/GRAPHIFY_INDEX_PLAN.md` — Complete indexing plan
- `AGENTS.md` — Graphify requirements for all agents
- `.opencode/agents/architect.md` — Architect's Graphify responsibilities
- `ADR-0001` — Platform architecture (indexed services)
