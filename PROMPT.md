You are starting Phase 0 of the Byrd Health project.

Before any implementation work begins, perform a complete architectural discovery and legacy analysis.

Read and follow:

- AGENTS.md
- PROMPT.md
- PROJECTPLAN.md
- PROJECT_IDEA.md
- .opencode/agents/architect.md

Your current objective is NOT to write code.

Your objective is to understand the existing fertility application under:

/legacy

and create the architectural foundation for the future Byrd Health platform.

---

## Phase 0 Goals

Analyze the legacy application and determine:

- What exists today.
- What works well.
- What should be preserved.
- What should be rewritten.
- What should be removed.
- What architectural lessons can be carried forward.

Do not modify legacy code.

Treat the legacy application as historical reference material.

---

## Required Deliverables

Create:

docs/LEGACY_REVIEW.md

Include:

- Existing technology stack
- Application structure
- Existing features
- Database design
- Business logic
- Fertility tracking logic
- User workflows
- Integrations
- Strengths
- Weaknesses
- Technical debt
- Security concerns
- Scalability concerns


Create:

docs/MIGRATION_PLAN.md

For every major component classify:

KEEP
REFACTOR
REWRITE
REMOVE

Explain the reasoning behind each decision.


Create:

docs/ARCHITECTURE_RECOMMENDATIONS.md

Recommend:

- Future service boundaries
- Backend architecture
- Frontend architecture
- Database strategy
- Home Assistant integration approach
- API strategy
- Device integration approach
- Future ByrdOS compatibility strategy


Create:

docs/GRAPHIFY_INDEX_PLAN.md

Identify:

- Important entities
- Services
- Modules
- Dependencies
- Relationships
- Architectural decisions
- Existing concepts that should be indexed

---

## Graphify Requirements

Before analysis:

Query Graphify for existing project knowledge.

After completing documents:

Prepare the Graphify updates required.

Do not leave architectural knowledge only inside markdown files.

---

## Agent Coordination

If additional expertise is required:

Recommend creation of specialist agents.

Do not create implementation tasks yet.

Do not begin coding.

---

## Completion Criteria

Phase 0 is complete when:

✓ Legacy application has been analyzed

✓ Migration decisions have been documented

✓ Future architecture recommendations exist

✓ Graphify indexing plan exists

✓ No production implementation has started

After completion, provide:

1. Summary of findings
2. Major architectural recommendations
3. Recommended next phase
4. Questions requiring user decisions