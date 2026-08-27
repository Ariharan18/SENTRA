# Smart Traffic Analytics — API Specification

## 1. Conventions

- Base path: `/api/v1`
- Media type: `application/json`
- Authorization header: `Authorization: Bearer <access_token>`
- Timestamp format: ISO 8601 UTC, such as `2026-08-27T08:30:00Z`
- List query parameters: `page` defaults to `1`; `page_size` defaults to `25` and may not exceed `100`.
- FastAPI OpenAPI documentation: `/docs`.

### Standard list response

```json
{
  "items": [],
  "page": 1,
  "page_size": 25,
  "total": 0
}
```

### Error response

```json
{
  "detail": "Human-readable error message"
}
```

Use `400` for business-rule failures, `401` for missing/invalid authentication, `403` for permission denial, `404` for missing resources, `409` for conflicts, and `422` for schema-validation failures.

## 2. Authentication and users

| Method | Path | Description | Access |
|---|---|---|---|
| POST | `/auth/login` | Authenticates and returns an access token. | Public |
| GET | `/auth/me` | Returns current user. | Authenticated |
| POST | `/auth/change-password` | Changes current user's password. | Authenticated |
| GET/POST | `/users` | Lists/creates users. | Admin |
| GET/PATCH | `/users/{id}` | Gets/updates user. | Admin; self for allowed fields |
| PATCH | `/users/{id}/status` | Activates/deactivates account. | Admin |

Login request:

```json
{
  "username": "operator@traffic.example",
  "password": "password"
}
```

Login response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## 3. Locations and sources

| Method | Path | Description |
|---|---|---|
| GET | `/locations` | List locations; filter by `q`, city, zone, source type, and active state. |
| POST | `/locations` | Create a location. |
| GET/PATCH | `/locations/{id}` | Get/update location. |
| POST | `/locations/{id}/archive` | Deactivate/archive location. |
| GET/POST | `/traffic-sources` | List/create traffic sources. |
| GET/PATCH | `/traffic-sources/{id}` | Get/update source. |

Location creation request:

```json
{
  "code": "JCT-001",
  "name": "Central Junction",
  "road_name": "Main Road",
  "junction_name": "Central Junction",
  "city": "Example City",
  "zone": "North",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "road_capacity": 500,
  "lane_count": 4,
  "speed_limit_kmh": 50
}
```

## 4. Traffic readings and imports

| Method | Path | Description |
|---|---|---|
| GET | `/traffic-readings` | Lists readings; filters include date range, location, city, zone, source, and congestion level. |
| POST | `/traffic-readings` | Creates a manual/API traffic reading. |
| GET | `/traffic-readings/{id}` | Gets a reading and its congestion record. |
| POST | `/traffic-readings/upload` | Uploads and validates a CSV import. |
| GET | `/traffic-imports` | Lists import history. |
| GET | `/traffic-imports/{id}` | Gets an import result and rejected rows. |

Traffic-reading request:

```json
{
  "location_id": 14,
  "source_id": 3,
  "recorded_at": "2026-08-27T08:30:00Z",
  "vehicle_count": 320,
  "average_speed_kmh": 18.5,
  "occupancy_percent": 82.0,
  "car_count": 220,
  "bike_count": 70,
  "bus_count": 20,
  "truck_count": 10,
  "emergency_count": 0
}
```

Import response:

```json
{
  "import_id": 8,
  "status": "Completed",
  "total_rows": 100,
  "accepted_rows": 97,
  "rejected_rows": 3
}
```

## 5. Congestion, alerts, and incidents

| Method | Path | Description |
|---|---|---|
| GET | `/congestion/current` | Latest congestion state by authorized location. |
| GET | `/congestion/trends` | Historical score/level data. |
| POST | `/congestion/recalculate` | Recalculates selected records after configuration change. |
| GET | `/alerts` | Lists alerts; filters by location, severity, status, and date. |
| GET/PATCH | `/alerts/{id}` | Gets or updates alert state. |
| POST | `/alerts/{id}/acknowledge` | Acknowledges an alert. |
| POST | `/alerts/{id}/resolve` | Resolves an alert with notes. |
| GET/POST | `/incidents` | Lists or creates incidents. |
| GET/PATCH | `/incidents/{id}` | Gets or updates incident. |
| POST | `/incidents/{id}/resolve` | Resolves an incident. |

## 6. Analytics and reporting

| Method | Path | Description |
|---|---|---|
| GET | `/analytics/summary` | KPI totals for selected filters. |
| GET | `/analytics/trends` | Traffic volume, speed, and score time series. |
| GET | `/analytics/by-location` | Location/road/zone comparisons. |
| GET | `/analytics/peak-hours` | Hour/day traffic and congestion heatmap data. |
| GET | `/analytics/vehicle-mix` | Vehicle-type distribution. |
| GET | `/analytics/status-distribution` | Congestion level distribution. |
| GET | `/reports/traffic.csv` | Filter-matched traffic export. |
| GET | `/reports/alerts.csv` | Filter-matched alert export. |
| GET | `/reports/incidents.csv` | Filter-matched incident export. |

Example request:

```text
GET /api/v1/analytics/summary?date_from=2026-08-01&date_to=2026-08-27&zone=North
```

Example response:

```json
{
  "active_locations": 42,
  "active_alerts": 6,
  "severe_locations": 3,
  "average_speed_kmh": 27.4,
  "total_vehicle_count": 108450
}
```

## 7. Administration and operations

| Method | Path | Description | Access |
|---|---|---|---|
| GET/POST | `/congestion-thresholds` | List/create threshold rules. | Admin |
| PATCH | `/congestion-thresholds/{id}` | Update threshold rule. | Admin |
| GET | `/audit-logs` | List/filter audit records. | Admin |
| GET | `/health` | Health/liveness check. | Public or infrastructure-only |

## 8. API implementation rules

- Use separate Pydantic create, update, and response schemas.
- Return `201 Created` for new resources and `204 No Content` only if no response body is needed.
- Apply authorization and data-scope filters in FastAPI services/dependencies, never only in Streamlit.
- Do not expose password hashes, tokens, configuration secrets, raw database errors, or internal tracebacks.
- Fully document routes, parameters, success/error models, and required roles through FastAPI OpenAPI metadata.
