# SENTRA – Implementation Steps

## 1. Purpose

This document is the implementation roadmap for SENTRA, an intelligent safety and threat detection platform.

Core features:
- Secure authentication
- User profiles and emergency contacts
- Emergency SOS
- Safety events
- Threat/risk detection
- Alerts
- Location-aware events
- Admin monitoring dashboard
- Analytics
- Audit logging

Use this document as the implementation order for the development team and AI coding assistants such as Antigravity.

## 2. Implementation Order

```text
Project Foundation
        ↓
Development Environment
        ↓
Backend Foundation
        ↓
Database
        ↓
Models & Schemas
        ↓
Authentication
        ↓
User Management
        ↓
Emergency Contacts
        ↓
Safety Events
        ↓
SOS
        ↓
Threat Detection
        ↓
Alerts
        ↓
Location
        ↓
Notifications
        ↓
Admin APIs
        ↓
Analytics
        ↓
Frontend
        ↓
Admin UI
        ↓
Integration
        ↓
Testing
        ↓
Security Hardening
        ↓
Deployment
```

Complete and test each phase before moving to the next.

---

# 3. Phase 0 – Project Initialization

Create:

```text
SENTRA/
```

Keep the documentation files in the root:

```text
README.md
SRS.md
SYSTEM_REQUIREMENTS.md
PROJECT_REQUIREMENTS.md
SYSTEM_ARCHITECTURE.md
DATABASE_SCHEMA.md
API_SPECIFICATION.md
DEVELOPMENT_RULES.md
SENTRA_IMPLEMENTATION_STEPS.md
```

Initialize Git:

```bash
git init
git add .
git commit -m "docs: add SENTRA project documentation"
```

Create `.gitignore` and exclude:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
node_modules/
dist/
build/
*.log
.idea/
.vscode/
```

Never commit credentials, tokens, API keys, or passwords.

---

# 4. Phase 1 – Development Environment

Install and verify:

- Python 3.x
- Node.js LTS
- npm
- MySQL 8+
- Git
- VS Code
- Postman

Verify:

```bash
python --version
node --version
npm --version
git --version
```

Make sure MySQL is running.

---

# 5. Phase 2 – Project Structure

Create:

```text
SENTRA/
├── README.md
├── SRS.md
├── SYSTEM_REQUIREMENTS.md
├── PROJECT_REQUIREMENTS.md
├── SYSTEM_ARCHITECTURE.md
├── DATABASE_SCHEMA.md
├── API_SPECIFICATION.md
├── DEVELOPMENT_RULES.md
├── SENTRA_IMPLEMENTATION_STEPS.md
├── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── core/
│   │   └── utils/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
├── database/
│   └── migrations/
└── tests/
```

Do not create unnecessary modules before they are required.

---

# 6. Phase 3 – Backend Foundation

Use Python + FastAPI.

Create a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

Install initial dependencies:

```bash
pip install fastapi uvicorn sqlalchemy pymysql python-dotenv pydantic pydantic-settings
```

Save dependencies:

```bash
pip freeze > requirements.txt
```

Create `backend/app/main.py`.

The first milestone is a working:

```http
GET /
```

Run:

```bash
uvicorn app.main:app --reload
```

Verify:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

Swagger must load successfully.

---

# 7. Phase 4 – Environment Configuration

Create `backend/.env`.

Example:

```env
APP_NAME=SENTRA
ENVIRONMENT=development
DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost:3306/sentra_db
SECRET_KEY=CHANGE_THIS
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Create `.env.example` without real credentials.

Never commit `.env`.

---

# 8. Phase 5 – Database

Create the database:

```sql
CREATE DATABASE sentra_db;
```

Connect FastAPI to MySQL through `database.py`.

Initial tables:

```text
users
emergency_contacts
events
alerts
locations
audit_logs
```

Follow `DATABASE_SCHEMA.md`.

Verify that the application can connect, read, write, and safely close database sessions.

---

# 9. Phase 6 – Models and Schemas

Create SQLAlchemy models:

```text
User
EmergencyContact
Event
Alert
Location
AuditLog
```

Create Pydantic schemas such as:

```text
UserCreate
UserLogin
UserResponse
ProfileUpdate
EmergencyContactCreate
EventCreate
EventResponse
AlertResponse
LocationCreate
```

Keep database models separate from API schemas.

---

# 10. Phase 7 – Authentication

Implement:

```http
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
```

Requirements:

- Validate input.
- Prevent duplicate email.
- Hash passwords.
- Never store plain-text passwords.
- Generate secure authentication tokens/sessions.
- Protect private endpoints.
- Support roles: `user` and `admin`.

Normal users must never be allowed to modify their own role.

---

# 11. Phase 8 – User Management

Implement:

```http
GET /api/users/profile
PUT /api/users/profile
```

Users can:

- View profile
- Update name
- Update phone
- Change password
- Manage emergency contacts

Users must only access their own private data.

---

# 12. Phase 9 – Emergency Contacts

Implement:

```http
POST /api/emergency-contacts
GET /api/emergency-contacts
PUT /api/emergency-contacts/{contact_id}
DELETE /api/emergency-contacts/{contact_id}
```

Requirements:

- Contact belongs to a user.
- Validate phone information.
- Prevent cross-user access.
- Protect contact information.

---

# 13. Phase 10 – Safety Events

Implement:

```http
POST /api/events
GET /api/events
GET /api/events/{event_id}
PUT /api/events/{event_id}
```

Event fields:

```text
event_id
user_id
event_type
risk_level
latitude
longitude
description
status
created_at
```

Risk levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Statuses:

```text
new
acknowledged
investigating
resolved
```

Add filtering and pagination for large event lists.

---

# 14. Phase 11 – SOS

Endpoint:

```http
POST /api/sos/trigger
```

When SOS is triggered:

1. Authenticate the user.
2. Receive available location.
3. Create an emergency event.
4. Set event type to `sos`.
5. Assign `CRITICAL` or configured emergency risk.
6. Store timestamp.
7. Create an alert.
8. Trigger configured notification services.
9. Return event and alert IDs.

Example response:

```json
{
  "message": "SOS activated",
  "event_id": 101,
  "alert_id": 201,
  "risk_level": "CRITICAL"
}
```

Protect against accidental duplicate SOS requests.

---

# 15. Phase 12 – Threat Detection

Create:

```text
backend/app/services/threat_detection.py
```

Start with rule-based detection.

Example:

```text
SOS event                    → CRITICAL
Configured serious event    → HIGH
Suspicious configured event → MEDIUM
Normal event                → LOW
```

Keep detection rules separate from API routes.

Do not claim the rule-based implementation is AI.

AI/ML can be integrated later.

---

# 16. Phase 13 – Alerts

Create alert generation logic.

Alert fields:

```text
alert_id
event_id
user_id
alert_type
priority
status
created_at
```

Implement:

```http
GET /api/alerts
PUT /api/alerts/{alert_id}
```

Statuses:

```text
new
acknowledged
investigating
resolved
```

Apply authentication and role-based authorization.

---

# 17. Phase 14 – Location

Support:

```text
latitude
longitude
timestamp
```

Requirements:

- Request appropriate client permission.
- Do not collect location unnecessarily.
- Validate latitude/longitude ranges.
- Associate location with authorized events.
- Protect location data.

For the first version, the frontend may send the available coordinates to the backend.

---

# 18. Phase 15 – Notifications

Create a notification abstraction:

```text
NotificationService
├── InAppNotification
├── EmailNotification
└── SMSNotification (future)
```

Start with in-app notifications.

Add external email/SMS providers only after the core event → alert flow works.

---

# 19. Phase 16 – Admin APIs

Implement admin-only endpoints:

```http
GET /api/admin/users
GET /api/admin/events
GET /api/admin/alerts
GET /api/admin/dashboard/summary
GET /api/admin/dashboard/analytics
```

Dashboard summary should include:

```text
total_users
active_alerts
total_events
critical_events
high_risk_events
resolved_events
```

Every admin endpoint must enforce the admin role.

---

# 20. Phase 17 – Analytics

Implement:

- Total events
- Events by risk level
- Events by type
- Events by day
- Active alerts
- Resolved alerts
- SOS count

Use database aggregation queries where possible.

---

# 21. Phase 18 – Frontend

Use React.

Recommended structure:

```text
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── services/
│   ├── hooks/
│   ├── context/
│   ├── utils/
│   └── App.jsx
├── package.json
└── ...
```

---

# 22. Phase 19 – Frontend Authentication

Create:

```text
/login
/register
```

Implement:

- Login
- Registration
- Logout
- Protected routes
- Role-based routes

Flow:

```text
User login  → User Dashboard
Admin login → Admin Dashboard
```

Never put backend secrets in frontend code.

---

# 23. Phase 20 – User UI

Create:

```text
Dashboard
Profile
Emergency Contacts
SOS
Events / History
Alerts
Settings
```

The SOS button must be clearly visible and easy to activate.

---

# 24. Phase 21 – Admin UI

Create:

```text
Admin Dashboard
Users
Events
Alerts
Threats
Analytics
Audit Logs
```

Display:

- Total users
- Active alerts
- Critical events
- High-risk events
- Recent events
- Risk distribution
- Event trends

Use charts where useful.

---

# 25. Phase 22 – Frontend/Backend Integration

Connect:

```text
Frontend
   ↓
REST API
   ↓
FastAPI
   ↓
MySQL
```

Verify:

- Registration
- Login
- Profile
- Emergency contacts
- Event creation
- SOS
- Alerts
- Admin dashboard

---

# 26. Phase 23 – Complete SOS Flow

The major SENTRA workflow must work end-to-end:

```text
User Login
    ↓
User Dashboard
    ↓
Press SOS
    ↓
Get available location
    ↓
POST /api/sos/trigger
    ↓
Create Event
    ↓
Threat Detection
    ↓
CRITICAL
    ↓
Create Alert
    ↓
Admin Dashboard
    ↓
Admin Acknowledges
    ↓
Investigates
    ↓
Resolves
```

This is a major project milestone.

---

# 27. Phase 24 – Audit Logging

Record important actions:

```text
USER_REGISTERED
USER_LOGIN
SOS_TRIGGERED
EVENT_CREATED
ALERT_CREATED
ALERT_ACKNOWLEDGED
ALERT_RESOLVED
ADMIN_VIEWED_EVENT
PROFILE_UPDATED
```

Never store passwords, tokens, or secrets in audit logs.

---

# 28. Phase 25 – Testing

Backend tests:

- Password hashing
- Authentication
- Risk classification
- Event creation
- SOS
- Alert generation
- Authorization

API tests:

```text
POST /auth/register
POST /auth/login
GET /users/profile
POST /events
POST /sos/trigger
GET /alerts
PUT /alerts/{id}
GET /admin/dashboard/summary
```

Security tests:

- Unauthenticated users cannot access protected APIs.
- Normal users cannot access admin APIs.
- Users cannot access another user's data.
- Invalid input is rejected.
- Password hashes are never returned.

Frontend tests:

- Login
- Registration
- Protected routes
- SOS
- Alerts
- Dashboard
- Admin access

---

# 29. Phase 26 – Error Handling

Use consistent errors.

Example:

```json
{
  "detail": "Unauthorized access"
}
```

Use appropriate status codes:

```text
200 OK
201 Created
400 Bad Request
401 Unauthorized
403 Forbidden
404 Not Found
409 Conflict
422 Validation Error
500 Internal Server Error
```

Never expose stack traces in production.

---

# 30. Phase 27 – Security Hardening

Before production:

- Secure password hashing
- HTTPS
- Protected environment variables
- Correct CORS configuration
- Input validation
- ORM/parameterized database queries
- Authorization checks
- Rate limiting where appropriate
- Dependency vulnerability review
- Restricted database access
- Database backups
- No secrets in logs

---

# 31. Phase 28 – Performance

Optimize:

- Database indexes
- Dashboard aggregation
- Event queries
- API response size
- Frontend rendering
- Database connections

Use pagination:

```text
GET /api/events?page=1&limit=20
```

Do not load the complete event history into memory unnecessarily.

---

# 32. Phase 29 – Documentation

Keep these documents updated:

```text
README.md
SRS.md
SYSTEM_REQUIREMENTS.md
PROJECT_REQUIREMENTS.md
SYSTEM_ARCHITECTURE.md
DATABASE_SCHEMA.md
API_SPECIFICATION.md
DEVELOPMENT_RULES.md
SENTRA_IMPLEMENTATION_STEPS.md
```

Update documentation whenever APIs, database tables, architecture, or major behavior changes.

---

# 33. Phase 30 – Deployment

Production architecture:

```text
User Browser
     ↓
HTTPS
     ↓
Frontend
     ↓
Reverse Proxy
     ↓
FastAPI Backend
     ↓
MySQL Database
     ↓
Notification Service
```

Production requirements:

- HTTPS
- Production environment variables
- Secure database credentials
- Database backups
- Logging
- Monitoring
- Error tracking
- Restricted database access

---

# 34. Phase 31 – Final Acceptance Testing

## Registration

```text
Register
→ validate
→ create account
→ securely store password
```

## Login

```text
Login
→ validate credentials
→ create authentication state
→ open dashboard
```

## SOS

```text
Press SOS
→ create event
→ capture available location
→ assign CRITICAL
→ create alert
→ admin sees alert
```

## Admin

```text
Admin login
→ dashboard
→ active threats visible
→ event details
→ acknowledge
→ investigate
→ resolve
```

## Authorization

```text
Normal user
→ admin API
→ 403 Forbidden
```

## Data Isolation

```text
User A
→ cannot access User B's private data
```

---

# 35. Definition of Done

A feature is complete only when:

- Code is implemented.
- Database changes are complete.
- API works.
- Authentication/authorization is verified.
- Validation exists.
- Error handling exists.
- Tests are added.
- Tests pass.
- Documentation is updated.
- No secrets are committed.
- Code follows `DEVELOPMENT_RULES.md`.

---

# 36. Recommended Milestones

## Milestone 1 – Foundation

```text
Project setup
FastAPI
MySQL
Database connection
```

## Milestone 2 – Authentication

```text
Registration
Login
Authentication
Roles
```

## Milestone 3 – User

```text
Profile
Emergency contacts
```

## Milestone 4 – Detection

```text
Events
Risk levels
Threat detection
```

## Milestone 5 – Emergency

```text
SOS
Alerts
```

## Milestone 6 – Location

```text
Location
Notifications
```

## Milestone 7 – Frontend

```text
React
User dashboard
```

## Milestone 8 – Admin

```text
Admin dashboard
Analytics
Audit logs
```

## Milestone 9 – Quality

```text
Testing
Security
Performance
```

## Milestone 10 – Release

```text
Deployment
Documentation
Final demo
```

---

# 37. Rules for Antigravity / AI Coding Assistant

When implementing SENTRA:

1. Read all Markdown documentation before modifying code.
2. Follow `SRS.md` for functional requirements.
3. Follow `SYSTEM_REQUIREMENTS.md` for system constraints.
4. Follow `SYSTEM_ARCHITECTURE.md` for architecture.
5. Follow `DATABASE_SCHEMA.md` for database design.
6. Follow `API_SPECIFICATION.md` for API conventions.
7. Follow `DEVELOPMENT_RULES.md` for coding and security rules.
8. Follow this document for implementation order.
9. Do not skip foundational phases.
10. Inspect existing code before changing it.
11. Do not rewrite working modules unnecessarily.
12. Do not introduce conflicting technologies without a clear reason.
13. Never hard-code credentials or secrets.
14. Never implement fake security.
15. Do not claim an AI/ML feature exists unless an actual model is integrated.
16. Keep modules small, reusable, and testable.
17. Run relevant tests after every major feature.
18. Update documentation when implementation changes documented behavior.
19. Preserve existing working functionality.
20. Do not create unnecessary files or dependencies.

---

# 38. AI Feature Implementation Workflow

For every feature:

```text
Read requirement
      ↓
Inspect existing code
      ↓
Identify affected modules
      ↓
Design change
      ↓
Implement backend/database
      ↓
Implement frontend
      ↓
Add validation
      ↓
Add authorization
      ↓
Add tests
      ↓
Run tests
      ↓
Fix errors
      ↓
Update documentation
      ↓
Commit changes
```

Do not generate large amounts of code without first understanding the existing project.

---

# 39. First Coding Task

At the beginning, implement only the foundation:

```text
Create project structure
        ↓
Create Python virtual environment
        ↓
Create FastAPI app
        ↓
Create MySQL database
        ↓
Connect FastAPI to MySQL
        ↓
Verify / and /docs
```

First checkpoint:

```text
SENTRA API is running
MySQL connection works
Swagger works
Project structure is clean
Git repository is initialized
```

Only after this checkpoint should authentication development begin.

---

# 40. Final Principle

SENTRA must be developed as a real, secure, maintainable application rather than a collection of demo screens.

Priority:

```text
Correctness
   ↓
Security
   ↓
Reliability
   ↓
Maintainability
   ↓
Usability
   ↓
Performance
   ↓
Advanced AI/ML
```

The core safety workflow must work reliably before advanced AI, IoT, or other future features are added.
