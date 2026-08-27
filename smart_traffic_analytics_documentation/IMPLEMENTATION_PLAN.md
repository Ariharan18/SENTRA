# Smart Traffic Analytics — Implementation Plan

## Phase 1 — Foundation and design

**Goal:** Establish project structure and confirm system rules.

1. Create the Git repository, backend/frontend directories, environment templates, and local Python/MySQL setup.
2. Configure FastAPI, Streamlit, MySQL, SQLAlchemy, Alembic, linting, and testing tools.
3. Finalize congestion formula, thresholds, user roles, input formats, and seed-data assumptions.
4. Create initial database ERD and API route inventory.

**Deliverables:** runnable empty services, `.env.example`, schema plan, and initial migration baseline.

## Phase 2 — Database and authentication

**Goal:** Deliver secure identity and core master data.

1. Implement roles, users, locations, traffic sources, and audit-log models.
2. Write Alembic migrations, foreign keys, constraints, and baseline indexes.
3. Seed Admin role/user and standard role records.
4. Implement password hashing, login, JWT authentication, current-user dependency, and role guards.
5. Build Streamlit login/logout and session handling.

**Exit criteria:** authorized users can sign in, protected APIs reject invalid users, and Admin can manage accounts and locations.

## Phase 3 — Traffic data ingestion

**Goal:** Store clean, traceable traffic readings.

1. Implement `traffic_readings` and import-history models.
2. Build create/list/detail endpoints with Pydantic validation and pagination.
3. Add source/location checks and duplicate-detection rules.
4. Implement CSV template download, upload parsing, validation, atomic persistence, and rejection reporting.
5. Build Streamlit traffic-reading form, upload page, and filtered data table.

**Exit criteria:** a valid CSV import stores readings; invalid rows are identified without corrupting accepted data.

## Phase 4 — Congestion, alerts, and incidents

**Goal:** Turn readings into actionable conditions.

1. Implement congestion-score calculation and configurable thresholds.
2. Persist congestion records and current location status.
3. Implement open/acknowledged/resolved alert lifecycle and duplicate-alert prevention.
4. Implement incident CRUD, status workflow, and links to locations/alerts.
5. Add audit events for threshold, alert, and incident changes.

**Exit criteria:** high/severe readings generate alerts and operators can resolve them with an audit trail.

## Phase 5 — Dashboard and analytics

**Goal:** Provide operational and historical decision support.

1. Implement summary, trend, breakdown, heatmap, ranking, and report APIs.
2. Build Streamlit live dashboard with KPIs, active-alert list, and congestion map.
3. Build historical analytics with filters, time-series charts, bar charts, heatmaps, and vehicle-type charts.
4. Add CSV export matching the selected, authorized filters.
5. Validate metrics against known test data.

**Exit criteria:** dashboard values, charts, and exports agree with MySQL test datasets.

## Phase 6 — Quality, deployment, and handover

**Goal:** Prepare a secure, reproducible release.

1. Add unit tests for services and integration tests for APIs, roles, imports, alerts, and analytics filters.
2. Add error handling, structured logging, health checks, and performance indexes.
3. Complete local Python/MySQL deployment configuration, backups, and migration procedures.
4. Execute security review: secrets, authorization, upload validation, logging, and CORS.
5. Prepare user guide, operations guide, API documentation, and demo data.

**Exit criteria:** all critical tests pass, migrations run from a clean database, and deployment/recovery instructions are verified.

## Milestones

| Milestone | Outcome |
|---|---|
| M1 | Repository, local environment, and base schema ready. |
| M2 | Authentication, roles, locations, and sources complete. |
| M3 | Traffic reading entry and CSV import complete. |
| M4 | Congestion, alerts, and incidents complete. |
| M5 | Analytics dashboard and reports complete. |
| M6 | Tests, local deployment, documentation, and handover complete. |

## Suggested implementation order

```text
Database migrations → authentication/RBAC → location/source management
→ traffic ingestion → congestion calculation → alerts/incidents
→ analytics APIs → Streamlit dashboards → tests → deployment
```
