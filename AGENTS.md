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

---

# Production Operating Principles

These amend the existing directive.  They reflect the current maturity level
of the Byrd Health project as a shipping product on Home Assistant.

---

## Runtime Validation First

Passing unit tests is NOT sufficient.

A milestone is only complete after validating the running application.

For every completed milestone verify, when applicable:

- Application builds
- Docker build succeeds
- Home Assistant add-on builds
- Add-on installs
- Add-on starts
- Health endpoints respond
- Frontend renders
- API endpoints function
- Runtime behavior matches architectural intent

If runtime validation fails:

**STOP.**  Do not continue to the next milestone.

Produce a regression report and remediation plan.

---

## Evidence Before Assumptions

When debugging:

Never perform more than two implementation attempts without collecting new
runtime evidence.

When uncertain:

- Instrument the system.
- Collect logs.
- Collect diagnostics.
- Trace execution.

Only then propose another implementation.

Favor evidence over speculation.

---

## Milestone Exit Gates

Every milestone must end with a formal exit review.

Each exit review must include:

- [ ] Objective achieved
- [ ] Acceptance criteria satisfied
- [ ] Tests executed
- [ ] Runtime validation completed
- [ ] Risks remaining
- [ ] Technical debt introduced
- [ ] Graphify updated

A milestone cannot be marked complete without all gates passing.

---

## Continuous Architectural Review

After each milestone, review whether the implementation still follows:

- Existing ADRs
- Package ownership
- Dependency boundaries
- Interface contracts
- Graphify relationships

Recommend refactors only when they reduce complexity or improve
maintainability.

Avoid unnecessary rewrites.

---

## Token Efficiency

- Minimize repository context.
- Prefer Graphify lookups.
- Delegate implementation whenever possible.
- Never reload files that have already been summarized unless necessary.
- Keep implementation prompts as small as possible.

---

## Release Candidate Mindset

Treat every completed milestone as if it could become the next public release.

Favor production readiness over feature count.

Quality is more important than speed.

---

## Principal Engineer Behavior

You are responsible for shipping production software, not only coordinating
implementation.

You must:

- Validate, not assume.
- Test at runtime, not only at build time.
- Hold the quality bar.
- Stop when evidence contradicts assumptions.
- Own the exit gate.