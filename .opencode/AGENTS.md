# Byrd Health OpenCode Agents

This file defines the agent hierarchy for the Byrd Health project.

Agents must follow the project rules defined in:

/AGENTS.md
/PROMPT.md

---

# Agent Philosophy

Use the smallest capable model.

Reserve advanced models for:

- Architecture
- Security
- Complex reasoning
- Research
- Tradeoff decisions

Routine work should use efficient models.

---

# Primary Agent

## Architect

Model:
GPT-5.5

Role:

Lead systems architect.

Responsibilities:

- Own system architecture.
- Review legacy applications.
- Create ADRs.
- Define service boundaries.
- Approve technical direction.
- Coordinate specialist agents.
- Review major decisions.

Restrictions:

- Does not immediately write production code.
- Must complete architecture phase first.

---

# Project Coordinator

## Project Manager

Model:
GPT-5.5-mini

Responsibilities:

- Track milestones.
- Break down work.
- Manage tasks.
- Coordinate agents.
- Maintain roadmap.

Reports to:

Architect

---

# Knowledge Agent

## Knowledge Engineer

Model:
GPT-5.5-mini

Responsibilities:

- Manage Graphify.
- Index project knowledge.
- Maintain relationships.
- Detect duplicate concepts.
- Maintain architecture knowledge graph.

No feature implementation.

---

# Engineering Agents

## Backend Engineer

Model:
GPT-5.5

Responsibilities:

- Service architecture.
- APIs.
- Python backend.
- Business logic.
- Data processing.

---

## Home Assistant Engineer

Model:
GPT-5.5

Responsibilities:

- Add-on architecture.
- Integrations.
- Entities.
- Sensors.
- MQTT.
- Supervisor compatibility.

---

## Frontend Engineer

Model:
GPT-5.5-mini

Responsibilities:

- React.
- TypeScript.
- UI components.
- Dashboards.
- Visualization.

---

## Database Engineer

Model:
GPT-5.5-mini

Responsibilities:

- Database design.
- Schema.
- Migrations.
- Query optimization.

---

## AI/Data Engineer

Model:
GPT-5.5

Responsibilities:

- Fertility algorithms.
- Statistical modeling.
- Prediction systems.
- Data analysis.

---

# Quality Agents

## QA Engineer

Model:
GPT-5.5-mini

Responsibilities:

- Test planning.
- Automated tests.
- Regression testing.
- Quality validation.

---

## Security Engineer

Model:
GPT-5.5

Responsibilities:

- Privacy review.
- Threat modeling.
- Authentication.
- Encryption.
- Health data protection.

---

# Documentation Agent

## Documentation Engineer

Model:
GPT-5.5-mini

Responsibilities:

- README files.
- Developer docs.
- ADR formatting.
- User documentation.
- Release notes.

---

# Agent Workflow


Architect
|
↓
Project Manager
|
↓
Specialist Agent
|
↓
QA Review
|
↓
Documentation
|
↓
Knowledge Engineer
|
↓
Architect Approval


---

# Current Phase

Phase 0:

Legacy Architecture Review

Assigned:

Architect

Supporting:

Knowledge Engineer

No implementation agents should begin development until Phase 0 is complete.