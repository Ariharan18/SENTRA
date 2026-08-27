# Smart Traffic Analytics and Congestion Monitoring System

Smart Traffic Analytics is a role-based application for monitoring road and intersection conditions. It ingests sensor, camera-metadata, CSV, or manual traffic data; calculates congestion; raises operational alerts; and provides current and historical analytics.

## Technology stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, FastAPI, SQLAlchemy, Pydantic |
| Frontend | Streamlit, Plotly, Pandas |
| Database | MySQL 8.0+ |
| Authentication | OAuth2 password flow and JWT |
| Deployment | Local Python services and MySQL |

## Core capabilities

- Role-based login for Admin, Traffic Operator, Analyst, and Viewer.
- Road, junction, sensor, and data-source management.
- Manual entry and CSV upload of traffic readings.
- Congestion scoring and Low, Moderate, High, or Severe classification.
- High/severe congestion alerts and incident management.
- Current monitoring, historical trend analysis, peak-hour analysis, analytics dashboard, and CSV reports.

## Proposed repository layout

```text
smart-traffic-analytics/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routers
│   │   ├── analytics/      # aggregation and congestion logic
│   │   ├── core/           # configuration and security
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # business logic
│   │   └── main.py
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── pages/
│   ├── services/           # FastAPI client and session helpers
│   ├── app.py
│   └── requirements.txt
├── .env.example
└── docs/
```

## Prerequisites

- Python 3.10 or later
- MySQL 8.0 or later
- Git
- A local MySQL 8.0+ installation and running service

## Local setup

1. Create the MySQL database and app account.

   ```sql
   CREATE DATABASE smart_traffic CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'traffic_user'@'localhost' IDENTIFIED BY 'change-this-password';
   GRANT ALL PRIVILEGES ON smart_traffic.* TO 'traffic_user'@'localhost';
   ```

2. Configure the project-root `.env`.

   ```dotenv
   APP_ENV=development
   DATABASE_URL=mysql+pymysql://traffic_user:change-this-password@localhost:3306/smart_traffic
   JWT_SECRET_KEY=replace-with-a-long-random-secret
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   CORS_ORIGINS=http://localhost:8501
   ```

3. Start FastAPI.

   ```bash
   cd backend
   python -m venv .venv
   # Windows PowerShell: .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn app.main:app --reload --port 8000
   ```

4. Start Streamlit in another terminal.

   ```bash
   cd frontend
   python -m venv .venv
   # Activate the virtual environment, then:
   pip install -r requirements.txt
   streamlit run app.py
   ```

Open API documentation at `http://localhost:8000/docs` and the dashboard at `http://localhost:8501`.

The dashboard includes filtered analytics, KPI summaries, traffic trends, congestion and vehicle distributions, location comparisons, peak-period analysis, and report downloads.

## Documentation

- `SRS.md` — complete system requirements.
- `PROJECT_REQUIREMENTS.md` — hardware, platform, package, and delivery requirements.
- `SYSTEM_ARCHITECTURE.md` — components, data flow, and deployment design.
- `DATABASE_SCHEMA.md` — entities, constraints, and indexes.
- `API_SPECIFICATION.md` — FastAPI REST contract.
- `DEVELOPMENT_RULES.md` — engineering, security, testing, and Git rules.
- `IMPLEMENTATION_PLAN.md` — staged project execution plan.

## Security

Never commit `.env` files, live credentials, JWT keys, uploads containing sensitive data, or database backups. Streamlit must call FastAPI for all data access, and FastAPI must enforce authorization independently of the interface.
