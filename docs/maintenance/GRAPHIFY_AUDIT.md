# Graphify Audit

Accuracy verification of the Graphify knowledge graph against the actual codebase.

## Summary: 15 Issues

| Severity | Count |
|----------|-------|
| Critical | 5 |
| High | 3 |
| Medium | 4 |
| Low | 3 |

---

## Critical (5)

1. **7 entity nodes missing** — `device-reading`, `cycle-phase`, `flow-value`, `mucus-value`, `opk-value`, `interpretation-method`, `temp-unit` have index entries but no corresponding files
2. **1 function node missing** — `enrich-insights-for-publishing` has index entry but no directory
3. **Phase-4 milestone missing** from index
4. **9 document nodes missing**
5. **5 entity nodes have wrong `key_fields`** vs actual SQLAlchemy model definitions

## High (3)

1. **3 document nodes reference markdown files that don't exist**
2. **4 nodes have reversed timestamps** (`created_at > updated_at`)
3. **3 edges target document nodes with no backing file**

## Medium (4)

1. **Agent naming inconsistency** — `Graphify Engineer` vs `knowledge-engineer`
2. **2 agents in Graphify not in AGENTS.md** — `AI Data Science`, `DevOps`
3. **Phase-2 status string inconsistency** — `"complete"` vs `"completed"`
4. **ADR-0006 governs empty** but edges show governance relationships

## Low (3)

1. **Fertility engine module name mismatch** — `cycle_analysis` vs `analysis`
2. **Phase-0 missing timestamps**
3. **Index `last_updated` is placeholder time**

## Verified Correct

- Services
- ADRs
- Concepts
- Integrations
- APIs
- No orphan files
- Edges structurally valid
