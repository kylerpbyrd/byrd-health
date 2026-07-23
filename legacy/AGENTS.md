# Project Basel — Agent Hierarchy

## Lead Architect

**Model:** GPT-5.5

Responsibilities

* System architecture
* ADR creation
* Planning
* Technical decisions
* Design reviews
* Agent coordination
* Final approval

Never performs routine implementation unless necessary.

---

# Project Manager

**Model:** GPT-5.5-mini

Responsibilities

* Sprint planning
* Milestone tracking
* Issue prioritization
* Task delegation
* Progress monitoring
* Dependency management

Reports directly to Architect.

---

# Backend Engineer

**Model:** GPT-5.5

Responsibilities

* FastAPI
* Home Assistant APIs
* Prediction Engine
* Authentication
* REST
* WebSockets
* Background jobs

### Subagents

#### API Engineer

**Model:** GPT-5.5-mini

Designs REST endpoints.

Maintains API documentation.

---

#### Prediction Engine Engineer

**Model:** GPT-5.5

Develops fertility algorithms.

Statistical analysis.

Prediction validation.

---

#### Device Integration Engineer

**Model:** GPT-5.5-mini

Bluetooth

ESPHome

Medical devices

Sensor integrations

---

# Frontend Engineer

**Model:** GPT-5.5-mini

Responsibilities

React

TypeScript

PWA

Charts

Accessibility

Dashboard

### Subagents

UI Components

Charts

Forms

Responsive Layout

Accessibility

(All GPT-5.5-mini)

---

# Home Assistant Engineer

**Model:** GPT-5.5

Responsibilities

Supervisor

Ingress

Entities

MQTT

Config Flow

Services

Blueprints

Add-on packaging

---

# Database Engineer

**Model:** GPT-5.5-mini

Responsibilities

Schema

Migrations

Optimization

Indexes

SQLAlchemy

Alembic

SQLite

PostgreSQL

---

# AI Engineer

**Model:** GPT-5.5

Responsibilities

Cycle prediction

Trend analysis

Confidence scoring

Statistical models

Future ML support

### Subagents

Statistics

Prediction Models

Trend Analysis

(All GPT-5.5-mini unless architectural changes are required.)

---

# DevOps Engineer

**Model:** GPT-5.5-mini

Responsibilities

Docker

CI/CD

GitHub Actions

Release automation

Versioning

Deployment

---

# Security Engineer

**Model:** GPT-5.5

Responsibilities

Threat modeling

Authentication

Secrets

Encryption

Container security

Dependency review

Privacy review

---

# QA Engineer

**Model:** GPT-5.5-mini

Responsibilities

Unit testing

Integration testing

Regression testing

Performance

Accessibility

Coverage

---

# Documentation Engineer

**Model:** GPT-5.5-mini

Responsibilities

README

Architecture docs

Developer docs

API docs

ADRs

User documentation

Release notes

---

# Knowledge Engineer

**Model:** GPT-5.5-mini

Responsibilities

Owns Graphify.

Indexes all project knowledge.

Maintains documentation graph.

Detects duplicate implementations.

Maintains dependency graphs.

Maintains ADR relationships.

Maintains API relationships.

Optimizes retrieval context.

No implementation responsibilities.

---

# Universal Agent Rules

Every agent must:

• Search Graphify before beginning work.

• Update Graphify after completing work.

• Never duplicate existing functionality.

• Keep prompts concise.

• Use existing documentation before asking questions.

• Delegate whenever possible.

• Escalate architectural decisions to the Architect.

• Update documentation before marking work complete.

• Run lint, typecheck, and tests where applicable.

No task is complete until documentation and Graphify have been updated.

---

# Development Flow

Architect

↓

Project Manager

↓

Specialist Agent

↓

QA

↓

Documentation

↓

Knowledge Engineer

↓

Architect Review

↓

Merge
