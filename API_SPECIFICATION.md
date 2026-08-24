# SENTRA – API Specification

## 1. API Overview

SENTRA uses REST APIs through the FastAPI backend.

Base URL for local development:

```text
http://127.0.0.1:8000/api
```

Production must use HTTPS.

## 2. Authentication

### Register

```http
POST /auth/register
```

Request:

```json
{
  "name": "Demo User",
  "email": "user@example.com",
  "phone": "9876543210",
  "password": "StrongPassword"
}
```

### Login

```http
POST /auth/login
```

Request:

```json
{
  "email": "user@example.com",
  "password": "StrongPassword"
}
```

Response:

```json
{
  "access_token": "TOKEN",
  "token_type": "bearer"
}
```

## 3. User APIs

### Get Profile

```http
GET /users/profile
Authorization: Bearer TOKEN
```

### Update Profile

```http
PUT /users/profile
Authorization: Bearer TOKEN
```

## 4. SOS APIs

### Trigger SOS

```http
POST /sos/trigger
Authorization: Bearer TOKEN
```

Example request:

```json
{
  "latitude": 13.0827,
  "longitude": 80.2707,
  "description": "Emergency assistance required"
}
```

Expected behavior:

- Create event
- Set high/critical risk
- Create alert
- Return event and alert identifiers

### SOS History

```http
GET /sos/history
Authorization: Bearer TOKEN
```

## 5. Event APIs

### Create Event

```http
POST /events
Authorization: Bearer TOKEN
```

### Get Events

```http
GET /events
Authorization: Bearer TOKEN
```

Optional filters:

```text
/events?risk_level=HIGH
/events?status=new
/events?event_type=sos
```

### Get Event

```http
GET /events/{event_id}
Authorization: Bearer TOKEN
```

### Update Event

```http
PUT /events/{event_id}
Authorization: Bearer TOKEN
```

## 6. Alert APIs

### Get Alerts

```http
GET /alerts
Authorization: Bearer TOKEN
```

### Update Alert

```http
PUT /alerts/{alert_id}
Authorization: Bearer TOKEN
```

Example:

```json
{
  "status": "acknowledged"
}
```

## 7. Dashboard APIs

### Dashboard Summary

```http
GET /dashboard/summary
Authorization: Bearer ADMIN_TOKEN
```

Example response:

```json
{
  "total_users": 100,
  "active_alerts": 5,
  "total_events": 250,
  "critical_events": 2,
  "resolved_events": 210
}
```

### Analytics

```http
GET /dashboard/analytics
Authorization: Bearer ADMIN_TOKEN
```

## 8. Standard HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 400 | Bad request |
| 401 | Authentication required/failed |
| 403 | Access denied |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation error |
| 500 | Server error |

## 9. API Security

- Use authentication for protected endpoints.
- Use role checks for admin endpoints.
- Validate request bodies.
- Never return password hashes.
- Do not expose secrets.
- Use HTTPS in production.
