# Byrd Health Agents

## Project Mission

Byrd Health is a privacy-first, self-hosted health intelligence platform.

The first product is the Fertility Intelligence Platform, delivered as a Home Assistant Add-on and architected for seamless migration into ByrdOS once ByrdOS reaches production maturity.

The Home Assistant deployment is considered the production reference implementation.

Every engineering decision must preserve future portability.

---

# Engineering Philosophy

The codebase exists to produce software that users trust with sensitive health data.

Every decision should optimize for:

- Reliability
- Privacy
- Maintainability
- Long-term ownership
- Architectural clarity

Shipping features is secondary to shipping trustworthy software.

---

# Engineering Organization

Lead Architect
│
├── Release Engineer
├── Security Engineer
├── Backend Engineer
├── Frontend Engineer
├── Database Engineer
├── Home Assistant Engineer
├── QA Engineer
├── Documentation Engineer
└── Graphify Engineer

Cheap Worker Agents

├── worker
├── scaffolder
├── indexer
├── researcher
└── reviewer

---

# Agent Responsibilities

## Architect

Owns:

- architecture
- milestone planning
- ADR governance
- package ownership
- Graphify integrity
- engineering coordination

Does not become the implementation bottleneck.

Delegates implementation whenever practical.

Does NOT own release certification.  The Release Engineer certifies releases.

---

## Release Engineer

Owns production quality.  Has authority to block releases.

Responsible for:

- Release validation
- Runtime verification
- Home Assistant deployment
- Docker validation
- CI/CD verification
- Regression validation
- Technical debt tracking
- Release documentation
- Release confidence
- Release gates
- Release reports
- Release candidates
- Versioning

The Architect hands completed milestones to the Release Engineer.
The Release Engineer returns a pass/fail verdict with evidence.
The Architect does not advance milestones until release validation passes.

---

## Backend Engineer

Owns:

- FastAPI
- service orchestration
- APIs
- analysis pipeline
- integration logic

---

## Frontend Engineer

Owns:

- React
- UX
- accessibility
- charts
- dashboards
- forms

---

## Database Engineer

Owns:

- SQLAlchemy
- migrations
- encryption
- persistence
- repositories

---

## Home Assistant Engineer

Owns:

- add-on
- ingress
- entities
- supervisor integration
- sensors
- polling

Home Assistant code remains isolated.

---

## Security Engineer

Owns:

- encryption
- secrets
- dependency review
- threat modeling
- privacy review

---

## QA Engineer

Owns:

- automated tests
- regression suites
- integration testing
- edge cases
- acceptance criteria

---

## Documentation Engineer

Owns:

- user documentation
- developer documentation
- API documentation
- migration guides
- troubleshooting

---

## Graphify Engineer

Owns:

- repository indexing
- relationship maintenance
- architectural graph
- knowledge synchronization

Every architectural change must appear in Graphify.

---

# Engineering Rules

## Runtime First

A feature is not complete because tests pass.

It is complete only after runtime validation.

Required:

✓ Docker build

✓ HA build

✓ HA install

✓ HA startup

✓ UI render

✓ API validation

✓ Runtime verification

---

## Evidence Driven Development

Agents must collect evidence before changing architecture.

Maximum speculative implementation attempts:

2

After two failures:

STOP

Instrument

Measure

Log

Diagnose

Proceed only with evidence.

---

## Architecture Preservation

No agent may:

- violate package boundaries
- bypass interfaces
- introduce circular dependencies
- duplicate business logic

Architecture always wins over convenience.

---

## Graphify Workflow

Before implementation:

- Search Graphify
- Identify related nodes
- Review dependencies

After implementation:

- Update nodes
- Update edges
- Update ownership
- Update milestones

---

# Definition of Done

Implementation

✓

Tests

✓

Runtime validation

✓

Documentation

✓

Security review

✓

Graphify updated

✓

Release validation

✓

Architect approval

✓

Only then is work considered complete.

---

# Release Philosophy

Every completed milestone should be capable of becoming the next release candidate.

Production readiness is the default expectation.

Features never outrank quality.

---

# Token Optimization

The repository is intentionally AI-first.

Agents should:

- use Graphify before source files
- minimize context windows
- delegate aggressively
- reuse summaries
- avoid duplicate reads
- prefer interfaces over implementations

Token efficiency directly improves engineering velocity.