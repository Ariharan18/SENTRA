# Smart Traffic Analytics — Project Requirements

## Hardware requirements

| Resource | Minimum development | Recommended development/production |
|---|---:|---:|
| CPU | 2 cores, 2.0 GHz | 4 cores, 2.5 GHz+ |
| Memory | 4 GB RAM | 8 GB RAM+ |
| Disk | 5 GB free | 20 GB SSD free |
| Network | Local/LAN connectivity | Stable Internet and HTTPS-enabled access |

## Software requirements

| Component | Requirement |
|---|---|
| Operating system | Windows 10/11, current Linux, or macOS |
| Python | Version 3.10 or later |
| Backend framework | FastAPI and Uvicorn |
| Frontend framework | Streamlit |
| Database | MySQL 8.0+ using `utf8mb4` |
| ORM | SQLAlchemy |
| Schema migrations | Alembic |
| Analytics | Pandas and SQLAlchemy aggregate queries |
| Visualization | Plotly and Streamlit charts |
| Security | OAuth2, JWT, bcrypt/Argon2 password hashing |
| Testing | Pytest and HTTPX |
| Deployment | Local Python services with a local MySQL 8.0+ service |

## Backend dependencies

```text
fastapi
uvicorn[standard]
sqlalchemy
pymysql
alembic
pydantic
pydantic-settings
python-jose[cryptography]
passlib[bcrypt]
python-multipart
python-dotenv
pandas
pytest
httpx
```

## Frontend dependencies

```text
streamlit
requests
pandas
plotly
python-dotenv
pytest
```

Use pinned package versions or a compatible lockfile for reproducible builds.

## Environment configuration

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLAlchemy MySQL connection string. |
| `JWT_SECRET_KEY` | High-entropy JWT signing secret. |
| `JWT_ALGORITHM` | Normally `HS256`. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry duration. |
| `APP_ENV` | `development`, `test`, or `production`. |
| `CORS_ORIGINS` | Approved Streamlit origin(s). |
| `MYSQL_DATABASE` | Local application database name. |
| `MYSQL_USER`, `MYSQL_PASSWORD` | Application MySQL credentials. |
| `CONGESTION_HIGH_THRESHOLD` | Default score that opens a high-congestion alert. |
| `CONGESTION_SEVERE_THRESHOLD` | Default score that opens a severe-congestion alert. |

## Data requirements

A valid traffic reading requires location, source, timestamp, vehicle count, average speed, and occupancy percentage. Optional fields include car, bike, bus, truck, and emergency-vehicle counts. Each location requires its capacity, speed limit, geographic coordinates, and active status.

## Delivery requirements

- FastAPI service with versioned REST APIs, OpenAPI documentation, and a health endpoint.
- Streamlit application with live dashboard, monitoring, data upload, alerts, incidents, analytics, reports, and administration pages.
- MySQL schema with foreign keys, validation constraints, indexes, seed data, and Alembic migrations.
- JWT authentication, backend-enforced authorization, audit logging, and safe error handling.
- Congestion calculation, alert creation, current-state queries, and historical analytics.
- Plotly/Streamlit visualizations: KPI cards, map, time series, heatmap, category charts, and ranked tables.
- CSV data ingestion with accepted/rejected-row feedback and CSV report exports.
- README, sample environment file, tests, and local deployment instructions.
