# SENTRA – System Requirements Specification

## 1. System Objective

SENTRA shall provide a centralized intelligent safety platform capable of monitoring events, detecting risks, generating alerts, recording incidents, and supporting authorized administrative monitoring.

## 2. System Components

### User Interface
Provides registration, login, dashboard, SOS, alerts, profile, event history, and location-aware features.

### Admin Interface
Provides user monitoring, event monitoring, alert management, analytics, reports, and system statistics.

### Backend Server
Responsible for authentication, authorization, business logic, event processing, threat evaluation, APIs, and database communication.

### Threat Detection Engine
Evaluates safety events using configurable rules and, in future versions, AI/ML models.

### Alert System
Creates prioritized alerts for important safety events.

### Database
Stores users, emergency contacts, events, alerts, locations, and audit logs.

## 3. Functional System Requirements

- SYS-FR-01: User registration
- SYS-FR-02: Authentication
- SYS-FR-03: Role management
- SYS-FR-04: User profile
- SYS-FR-05: Emergency SOS
- SYS-FR-06: Event creation
- SYS-FR-07: Threat detection
- SYS-FR-08: Real-time/near-real-time monitoring
- SYS-FR-09: Alert generation
- SYS-FR-10: Alert status management
- SYS-FR-11: Location management
- SYS-FR-12: Event management
- SYS-FR-13: Dashboard
- SYS-FR-14: Analytics
- SYS-FR-15: Event history

## 4. Hardware Requirements

### Client
- Desktop, laptop, tablet, or smartphone
- 2 GB RAM or higher recommended
- Modern web browser
- Internet connection

### Server
- 4 GB RAM or higher recommended
- Multi-core processor
- At least 20 GB available storage for development
- Stable network connection

## 5. Software Requirements

- Windows, Linux, or macOS
- Python 3.x
- FastAPI
- Uvicorn
- MySQL
- HTML/CSS/JavaScript or React
- Git
- Postman
- VS Code or PyCharm

## 6. Network Requirements

- HTTP/HTTPS
- REST API communication
- Secure authentication
- Client-server connectivity
- Database-server connectivity

HTTPS is required for production deployment.

## 7. Performance Requirements

- Normal APIs should respond promptly.
- Emergency events should be processed with minimal delay.
- Dashboard queries should be optimized.
- Database indexes should be used for frequently searched fields.

## 8. Security Requirements

- Password hashing
- Authentication
- Role-based access control
- Input validation
- API authorization
- Audit logging
- Secure error handling
- HTTPS in production

## 9. Backup and Recovery

- Regular database backups
- Recovery procedures
- Error logging
- Database restoration
- Protection against loss of important event records

## 10. System Constraints

- Internet availability may affect online features.
- Location services may be unavailable.
- Third-party notification services may have limits.
- Detection quality depends on available data.
