# SENTRA – Project Requirements

## 1. Project Overview

SENTRA is a safety and threat detection platform that connects users, a backend service, a database, a threat detection component, an alert system, and an administrative dashboard.

## 2. Project Goals

1. Provide a simple safety interface.
2. Enable emergency SOS.
3. Detect and classify safety risks.
4. Generate timely alerts.
5. Maintain structured event records.
6. Provide centralized monitoring.
7. Provide analytics for administrators.
8. Build a scalable foundation for AI and IoT extensions.

## 3. User Requirements

Users should be able to:

- Register
- Log in
- Manage their profile
- Add emergency contacts
- Trigger SOS
- Submit or view safety events
- Receive alerts
- View relevant history
- Manage permissions

## 4. Administrator Requirements

Administrators should be able to:

- Log in securely
- Monitor users
- View active events
- View risk levels
- Manage alerts
- Update event status
- Search and filter events
- View analytics
- Review audit logs

## 5. Core Functional Requirements

### Authentication
Secure registration, login, logout, and role management.

### SOS
Emergency activation with event creation, timestamp, available location, and alert generation.

### Threat Detection
Risk classification using configurable rules, with AI/ML planned for future versions.

### Event Management
Creation, retrieval, filtering, status updates, and resolution.

### Alert Management
Generation, prioritization, acknowledgement, investigation, and resolution.

### Dashboard
Summary cards, recent events, active alerts, and risk statistics.

## 6. Non-Functional Requirements

- Security
- Performance
- Reliability
- Availability
- Scalability
- Usability
- Maintainability

## 7. Data Requirements

The project shall store:

- User data
- Emergency contacts
- Safety events
- Alerts
- Locations
- Risk levels
- Status information
- Audit logs
- Timestamps

## 8. Technology Requirements

Recommended stack:

- Frontend: React or HTML/CSS/JavaScript
- Backend: Python + FastAPI
- Database: MySQL
- Authentication: JWT or secure sessions
- Testing: Pytest and Postman
- Version control: Git/GitHub

## 9. Project Deliverables

- Source code
- Database schema
- REST APIs
- Frontend
- Admin dashboard
- Tests
- Documentation
- Deployment configuration

## 10. Acceptance Criteria

The project will be considered ready for its initial release when:

- Users can register and log in.
- Authentication is secure.
- SOS creates an emergency event.
- Events are stored correctly.
- Risk levels are assigned.
- Alerts are generated.
- Administrators can monitor events.
- Dashboard statistics work.
- APIs return valid responses.
- Database operations are reliable.
