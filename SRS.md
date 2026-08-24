# SENTRA – Software Requirements Specification (SRS)

## 1. Introduction

### 1.1 Purpose

SENTRA is an intelligent safety monitoring platform designed to identify potential risks, manage emergency situations, generate alerts, and provide centralized monitoring.

### 1.2 Scope

SENTRA provides:

- User registration and authentication
- User profile management
- Safety monitoring
- Threat detection
- Emergency SOS
- Location-aware events
- Alerts and notifications
- Incident/event recording
- Admin monitoring
- Reports and analytics

### 1.3 Intended Users

#### Users
- Register and log in
- Manage their profile
- Trigger SOS
- Receive alerts
- View safety history

#### Administrators
- Monitor users and events
- View detected threats
- Manage incidents
- Review alerts
- View reports and analytics

## 2. Functional Requirements

### FR-01 User Registration
The system shall allow users to create accounts using validated information.

### FR-02 User Login
The system shall authenticate registered users and reject invalid credentials.

### FR-03 Profile Management
Users shall be able to view and update profile and emergency-contact information.

### FR-04 Safety Monitoring
The system shall monitor supported safety-related information and assign risk levels when sufficient information is available.

### FR-05 Threat Detection
The system shall identify potentially risky or abnormal situations and classify them as LOW, MEDIUM, HIGH, or CRITICAL.

### FR-06 SOS
When SOS is triggered, the system shall create an emergency event, record timestamp and available location, assign high priority, and generate an alert.

### FR-07 Alert Management
The system shall generate and manage alerts with statuses such as New, Acknowledged, Investigating, and Resolved.

### FR-08 Event Management
Administrators shall be able to view, search, filter, update, and resolve events.

### FR-09 Location Management
The system shall store available latitude, longitude, and timestamp information for authorized safety-related functions.

### FR-10 Admin Dashboard
The dashboard shall show users, active alerts, threats, emergency events, resolved events, and statistics.

### FR-11 Analytics
The system shall provide event counts, risk distribution, emergency statistics, and resolved/unresolved statistics.

### FR-12 Search and Filtering
Administrators shall be able to filter events by user, type, risk, status, date, and location.

### FR-13 Event History
The system shall maintain historical safety events.

### FR-14 Notifications
The system may notify authorized recipients through configured channels such as in-app notifications, email, or SMS.

### FR-15 Logout
Users and administrators shall be able to securely log out.

## 3. Non-Functional Requirements

### Performance
The system should respond quickly and process emergency events with minimal delay.

### Security
The system shall use authentication, password hashing, authorization, input validation, and secure data handling.

### Reliability
The system should prevent unnecessary data loss and handle errors gracefully.

### Scalability
The architecture should support increasing users, events, alerts, and data volume.

### Usability
The interface should be simple, responsive, and easy to understand during urgent situations.

### Maintainability
The system should use modular components.

## 4. Constraints

- Some features require internet connectivity.
- Location-based features require location availability and permission.
- Notification channels may require third-party services.
- Detection accuracy depends on available data.

## 5. Future Enhancements

- AI/ML threat prediction
- IoT integration
- Wearable integration
- Advanced geofencing
- Voice emergency activation
- Mobile application
- Offline support
