# SENTRA – System Architecture

## 1. Architecture Overview

SENTRA follows a modular client-server architecture.

```text
+----------------------+
|      User / Admin    |
+----------+-----------+
           |
           v
+----------------------+
|    Frontend / UI     |
+----------+-----------+
           |
        HTTPS/REST
           |
           v
+----------------------+
|   FastAPI Backend    |
+----------+-----------+
           |
    +------+------+
    |             |
    v             v
+---------+   +----------------+
| Threat  |   | Authentication |
| Engine  |   | & Authorization|
+----+----+   +----------------+
     |
     v
+----------------------+
|      MySQL DB        |
+----------+-----------+
           |
           v
+----------------------+
|    Alert Service     |
+----------------------+
```

## 2. Architectural Layers

### Presentation Layer
Responsible for web pages, forms, dashboards, charts, alerts, and user interaction.

### API Layer
Provides REST endpoints and validates requests.

### Business Logic Layer
Handles users, events, SOS, alerts, risk evaluation, and analytics.

### Detection Layer
Processes event information and assigns risk levels.

### Data Access Layer
Handles database queries and transactions.

### Database Layer
Stores persistent application data.

## 3. Main Modules

### Authentication Module
- Registration
- Login
- Logout
- Token/session validation
- Role checks

### User Module
- Profile
- Emergency contacts
- Preferences

### SOS Module
- SOS trigger
- Emergency event creation
- Priority assignment
- Alert generation

### Threat Detection Module
- Input processing
- Rule evaluation
- Risk classification

### Event Module
- Event creation
- Search
- Filtering
- Status management

### Alert Module
- Alert generation
- Priority
- Acknowledgement
- Resolution

### Dashboard Module
- Summary
- Live/near-live monitoring
- Analytics

## 4. Data Flow

```text
User Action
    |
    v
Frontend
    |
    v
API Request
    |
    v
Authentication
    |
    v
Business Logic
    |
    v
Threat Evaluation
    |
    +----> Low/Medium --> Record Event
    |
    +----> High/Critical --> Record Event + Generate Alert
                                      |
                                      v
                               Admin Dashboard
```

## 5. Deployment Architecture

Development:

```text
Browser
  |
  +--> Frontend
  |
  +--> FastAPI :8000
             |
             +--> MySQL
```

Production can use:

- Frontend hosting
- Reverse proxy
- FastAPI application server
- Managed MySQL
- HTTPS
- Monitoring and backups

## 6. Scalability

The architecture should support:

- Stateless API instances
- Database indexing
- Connection pooling
- Caching when required
- Background jobs for notifications
- Separate services for AI/ML in future

## 7. Security Architecture

- HTTPS
- Password hashing
- JWT/session authentication
- Role-based authorization
- Input validation
- Secure database credentials
- Audit logging
- Environment variables for secrets
