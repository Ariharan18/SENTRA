# SENTRA

## Intelligent Safety & Threat Detection Platform

SENTRA is an intelligent safety monitoring platform designed to detect potential risks, manage emergency situations, generate alerts, and provide centralized monitoring for authorized administrators.

## Key Features

- User registration and authentication
- User profile and emergency contact management
- Emergency SOS
- Safety event creation and management
- Threat/risk detection
- Risk levels: LOW, MEDIUM, HIGH, CRITICAL
- Real-time or near-real-time monitoring
- Alert generation and management
- Location-aware safety events
- Admin dashboard
- Analytics and reports
- Event history
- Audit logging
- Future support for AI/ML and IoT

## Technology Stack

- Frontend: HTML, CSS, JavaScript / React
- Backend: Python, FastAPI, Uvicorn
- Database: MySQL
- API Testing: Postman
- Development: VS Code / PyCharm, Git, GitHub

## System Flow

User → Frontend → FastAPI Backend → Threat Detection → Database → Alert System → Admin Dashboard

## Main Modules

1. Authentication
2. User Management
3. Emergency SOS
4. Threat Detection
5. Event Management
6. Alert Management
7. Location Management
8. Admin Dashboard
9. Analytics
10. Audit Logs

## Basic Setup

1. Clone the project.
2. Create and activate a Python virtual environment.
3. Install backend dependencies.
4. Configure MySQL credentials using environment variables.
5. Create the SENTRA database.
6. Start the FastAPI server.
7. Start the frontend.
8. Open the application in a browser.

Example backend command:

```bash
uvicorn main:app --reload
```

## Project Structure

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
├── backend/
├── frontend/
├── database/
└── tests/
```

## Security

Passwords must be hashed. APIs must validate input and enforce authentication and role-based authorization. HTTPS should be used in production.

## Future Enhancements

- AI-based anomaly detection
- Machine-learning risk prediction
- IoT sensor integration
- Smartwatch/wearable integration
- Geofencing
- Voice-based emergency activation
- Mobile application
- Offline emergency support
- Real-time maps
- Multilingual support
