# Smart Traffic Analytics — Development Rules

## 1. Core principles

- FastAPI is the source of truth for business rules, congestion calculation, authorization, and database access.
- Streamlit is a user-interface layer only; it must not access MySQL directly.
- Prefer focused, readable, testable code over premature abstraction.
- Preserve operational history and auditability for critical changes.
- Keep secrets, sensitive uploads, and production data out of source control.

## 2. Python and FastAPI rules

- Use Python 3.10+ and type hints for public functions, router handlers, and services.
- Follow PEP 8; format with Black/Ruff and keep imports ordered.
- Structure backend modules as `api`, `schemas`, `services`, `models`, `repositories`, `analytics`, and `core`.
- Use distinct Pydantic create, update, and response schemas; do not serialize ORM models directly.
- Keep routers thin and place business rules in service functions/classes.
- Use FastAPI dependencies for database sessions and authenticated-user context.
- Use explicit transaction boundaries and roll back failed multi-record writes/imports.
- Return correct, stable HTTP errors without exposing stack traces.
- Use async endpoints only when dependencies are genuinely asynchronous.

## 3. Traffic-data and analytics rules

- Validate location/source active state, timestamp, counts, speed, occupancy, and duplication before persistence.
- Treat raw traffic readings as historical facts; use an auditable correction mechanism rather than silent overwrite.
- Version the congestion formula and threshold configuration used by each calculated record.
- Ensure all dashboard aggregate queries are limited to the user's authorized scope and selected filters.
- Test scoring boundaries, including zero traffic, full occupancy, low speed, missing optional vehicle counts, and threshold transitions.
- Keep peak-hour, ranking, and trend computations in the backend/SQL layer rather than duplicating calculation logic in Streamlit.

## 4. Database rules

- Use SQLAlchemy parameterized queries; never concatenate user input into SQL.
- Manage every schema change through Alembic migrations.
- Use UTC timestamps; use fixed-point `DECIMAL` where numeric precision matters.
- Add indexes matching production filtering and aggregation paths.
- Use foreign keys and database/application constraints to protect integrity.
- Deactivate/archive referenced entities instead of hard-deleting history.
- Make audit logs append-only and omit passwords, JWTs, and secrets from JSON change summaries.

## 5. Security rules

- Hash passwords using bcrypt or Argon2; never store recoverable passwords.
- Enforce JWT validity, active-user state, roles, and scope in FastAPI.
- Keep configuration in environment variables using `pydantic-settings`.
- Maintain `.env.example`; include `.env`, backups, uploads, exported reports, logs, virtual environments, and credentials in `.gitignore`.
- Restrict CORS to permitted frontend origins in production and require HTTPS.
- Do not put tokens in URLs, display them, or record them in logs.
- Validate CSV MIME type, file size, headers, and each row before accepting imports.

## 6. Streamlit rules

- Centralize API calls in a frontend service/client module.
- Keep access tokens only in Streamlit server-side session state.
- Hide inaccessible navigation for usability but rely on FastAPI for enforcement.
- Handle loading, empty, validation-error, request-error, and successful states.
- Use `st.cache_data` only for safe read operations and clear/invalidate cached values after mutations.
- Use accessible Plotly charts with visible titles, axes, units, legends, and non-color severity labels.
- Do not put business calculations, database credentials, or raw SQL in Streamlit pages.

## 7. Testing rules

- Unit-test services for scoring, threshold, alert, incident, and import business rules.
- Integration-test authentication, role enforcement, CRUD APIs, pagination, filters, exports, and CSV import transaction behavior.
- Test successful, invalid, unauthenticated, and unauthorized paths for every protected module.
- Use a separate test database or transaction-isolated test fixture; never test against production data.
- Add regression tests for every confirmed defect.
- A critical feature is not complete until automated tests and its manual acceptance path both pass.

## 8. Git, review, and release rules

- Use focused branches and small, imperative commits, for example `Add congestion score service`.
- Never commit generated data, private map/API keys, credentials, database dumps, or virtual environments.
- Pull requests must state the purpose, tests, database migration, configuration impact, security impact, and rollback method when relevant.
- Reviewers must examine authorization, input validation, indexes, migrations, and audit-log impact for data-facing changes.
- Release only after migrations run successfully against a clean environment, tests pass, backups are configured, and monitoring/health checks are verified.

## 9. Definition of done

A feature is complete only when it meets the documented requirement, has backend authorization and validation, includes required migrations/indexes, handles UI states, adds audit data where applicable, passes relevant tests, updates API documentation, and has no unaddressed security/deployment impact.
