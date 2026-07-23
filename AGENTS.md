# Byrd Health Agents

## Project Mission

Byrd Health is a privacy-first, self-hosted health intelligence platform.

The first service is fertility intelligence, initially deployed as a Home Assistant Add-on and designed for future integration with ByrdOS when ByrdOS reaches production maturity.

The project must remain independent from ByrdOS during development.

---

# Core Engineering Principles

## Privacy First

Health data is sensitive.

Agents must:

- Prefer local processing.
- Avoid unnecessary data collection.
- Never transmit health data externally without explicit architecture approval.
- Avoid vendor lock-in.
- Document every data flow.

---

## Architecture First

No production implementation begins before architecture approval.

Before writing code:

- Understand requirements.
- Review existing systems.
- Document decisions.
- Create ADRs when necessary.
- Define boundaries.

---

## Modular Design

Services must be:

- Replaceable.
- Independently testable.
- Clearly documented.
- Portable.

Business logic must not depend on deployment environments.

Home Assistant is a deployment target.

ByrdOS is a future integration target.

---

# Agent Workflow


Architect
|
↓
Planning
|
↓
Specialist Agents
|
↓
QA Review
|
↓
Documentation
|
↓
Graphify Update
|
↓
Architect Approval


---

# Legacy Code Rules

The legacy fertility application is reference material only.

Legacy code must not be directly migrated.

Before reuse:

1. Analyze the implementation.
2. Document strengths.
3. Document weaknesses.
4. Identify reusable concepts.
5. Decide KEEP, REFACTOR, REWRITE, or REMOVE.

---

# Graphify Requirements

Graphify is part of the development workflow.

Agents must:

Before work:
- Search existing knowledge.
- Identify related decisions.
- Avoid duplicate implementations.

After work:
- Update relationships.
- Index decisions.
- Record dependencies.

Graphify should contain:

- Architecture decisions.
- Services.
- APIs.
- Database models.
- Dependencies.
- Documentation relationships.

---

# Definition of Done

A task is complete only when:

✓ Implementation completed

✓ Tests pass

✓ Documentation updated

✓ ADR created if required

✓ Graphify updated

✓ Security considerations reviewed

✓ Architect approval obtained