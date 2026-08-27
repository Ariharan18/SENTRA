# Software Requirements Specification

## Smart Traffic Analytics and Congestion Monitoring System

## 1. Introduction

### 1.1 Purpose

The system collects and analyzes traffic data from monitored roads and intersections. It calculates congestion, creates alerts, records incidents, and presents real-time and historical data for traffic-management personnel.

### 1.2 Scope

The initial release supports sensor/camera metadata, manual entry, and CSV uploads. It covers traffic locations, sources, readings, congestion records, alerts, incidents, analytics, reports, users, roles, and audit logs. It does not store camera video, control traffic signals, process public payments, or provide native mobile apps.

### 1.3 Definitions

| Term | Meaning |
|---|---|
| Traffic reading | Timestamped measurement of traffic volume, speed, and occupancy. |
| Location | Monitored road segment, intersection, or junction. |
| Congestion score | Numerical severity measurement on a normalized 0–100 scale. |
| Alert | Operational notification raised for a qualifying traffic condition. |
| Incident | Accident, roadwork, failure, or other road disruption. |

## 2. Product overview

### 2.1 User roles

| Role | Access |
|---|---|
| Admin | Users, roles, master data, locations, thresholds, audit logs, and all system data. |
| Traffic Operator | Traffic readings, active monitoring, alerts, incidents, and permitted reports. |
| Analyst | Dashboard, historical analytics, and permitted exports. |
| Viewer | Read-only dashboard and authorized traffic data. |

### 2.2 Operating environment

FastAPI runs the API and calculation services. Streamlit presents the user interface. MySQL 8 stores persistent relational data. A current desktop browser accesses Streamlit. The system runs in a local Python development environment with a local MySQL service.

## 3. Functional requirements

### 3.1 Authentication and access control

| ID | Requirement |
|---|---|
| FR-AUTH-001 | The system shall authenticate users using email/username and password. |
| FR-AUTH-002 | The backend shall store passwords only as secure hashes and return expiring JWT access tokens after valid authentication. |
| FR-AUTH-003 | The backend shall reject protected requests without a valid JWT and enforce role/scope permissions. |
| FR-AUTH-004 | Admins shall create, activate, deactivate, reset, search, and assign roles to users. |
| FR-AUTH-005 | Users shall update their own profiles and passwords. |
| FR-AUTH-006 | Inactive users shall not authenticate or receive new assignments. |
| FR-AUTH-007 | The system shall audit failed logins and account/role status changes. |

### 3.2 Location and traffic source management

| ID | Requirement |
|---|---|
| FR-LOC-001 | Authorized users shall create and update monitored locations. |
| FR-LOC-002 | A location shall include name, road, junction, city/zone, latitude, longitude, capacity, lane count, speed limit, and active status. |
| FR-LOC-003 | The system shall search/filter locations by city, zone, road, source type, and status. |
| FR-LOC-004 | Locations containing historic readings shall be archived/deactivated rather than deleted. |
| FR-SRC-001 | Admins shall manage source records containing source type, identifier, linked location, and active status. |
| FR-SRC-002 | Supported source types shall include Sensor, Camera Metadata, CSV Upload, Manual Entry, and API Integration. |
| FR-SRC-003 | Each traffic reading shall retain the source that produced it. |

### 3.3 Traffic-reading ingestion

| ID | Requirement |
|---|---|
| FR-TRF-001 | Authorized users and integrations shall create traffic readings. |
| FR-TRF-002 | A reading shall contain location, source, timestamp, vehicle count, average speed, and occupancy percentage. |
| FR-TRF-003 | The system shall optionally store car, bike, bus, truck, and emergency-vehicle counts. |
| FR-TRF-004 | The system shall validate non-negative counts/speeds and occupancy between 0 and 100. |
| FR-TRF-005 | The system shall reject readings for inactive locations or sources. |
| FR-TRF-006 | The system shall support CSV upload and validate every row. |
| FR-TRF-007 | An import shall return accepted and rejected counts plus row-level rejection reasons. |
| FR-TRF-008 | The system shall reject duplicate readings from the same source, location, and timestamp unless an authorized correction is supplied. |
| FR-TRF-009 | The system shall retain upload file name, uploader, date, and result summary. |
| FR-TRF-010 | Users shall filter readings by time, location, zone, source, and congestion level. |

### 3.4 Congestion analysis

| ID | Requirement |
|---|---|
| FR-CONG-001 | The system shall calculate and persist a congestion score and level for every valid reading. |
| FR-CONG-002 | The calculation shall evaluate traffic volume/capacity, average speed/speed limit, and occupancy. |
| FR-CONG-003 | Admins shall configure Low, Moderate, High, and Severe thresholds. |
| FR-CONG-004 | The system shall calculate congestion immediately after persisting a reading. |
| FR-CONG-005 | The system shall provide the latest congestion state for every active location. |
| FR-CONG-006 | The system shall identify peak hours and top-congested locations over selected filters. |
| FR-CONG-007 | Authorized recalculation following threshold changes shall be logged. |

Default normalized score:

```text
(vehicle_count / road_capacity × 40)
+ (1 - average_speed / speed_limit × 35)
+ (occupancy_percent / 100 × 25)
```

| Score | Level |
|---:|---|
| 0–25 | Low |
| 26–50 | Moderate |
| 51–75 | High |
| 76–100 | Severe |

### 3.5 Alerts and incidents

| ID | Requirement |
|---|---|
| FR-ALERT-001 | The system shall create an alert when configured High or Severe conditions are met. |
| FR-ALERT-002 | Alerts shall store location, severity, score, generated time, description, status, and resolution data. |
| FR-ALERT-003 | Alert statuses shall be Open, Acknowledged, Resolved, or Closed. |
| FR-ALERT-004 | Traffic Operators shall acknowledge and resolve alerts. |
| FR-ALERT-005 | The system shall prevent duplicate active alerts for the same location and condition. |
| FR-ALERT-006 | The dashboard shall highlight active High and Severe alerts. |
| FR-INC-001 | Authorized users shall create, update, list, and resolve incidents. |
| FR-INC-002 | Incidents shall include location, type, severity, reported time, description, status, reporter, and resolution notes. |
| FR-INC-003 | Types shall include Accident, Roadwork, Vehicle Breakdown, Signal Failure, Weather Condition, and Other. |
| FR-INC-004 | The system shall show active incidents on monitoring views and may link them to alerts. |

### 3.6 Analytics, reporting, and auditing

| ID | Requirement |
|---|---|
| FR-ANL-001 | The dashboard shall show active locations, alert count, severe locations, average speed, and vehicle-volume KPIs. |
| FR-ANL-002 | Users shall filter data by date range, city, zone, location, source, and congestion level. |
| FR-ANL-003 | The dashboard shall show a congestion map, traffic/congestion time series, comparison bar charts, peak-time heatmap, and vehicle-type distribution. |
| FR-ANL-004 | The dashboard shall show congestion-status distribution and ranked congested-location tables. |
| FR-ANL-005 | All charts shall update in response to filter changes. |
| FR-REP-001 | Users shall produce traffic-reading, congestion, alert, incident, and peak-hour reports. |
| FR-REP-002 | Authorized users shall export filter-matching CSV reports. |
| FR-AUD-001 | The system shall audit critical creates, updates, imports, exports, configuration changes, acknowledgements, and resolutions. |
| FR-AUD-002 | Audit entries shall record actor, timestamp, action, entity type/ID, and a safe change summary. |
| FR-AUD-003 | Only Admins shall view full audit logs. |

## 4. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-001 | Typical API responses shall complete in under 2 seconds; normal dashboard filters in under 5 seconds. |
| NFR-002 | Lists shall paginate; indexes shall support time, location, source, status, and congestion queries. |
| NFR-003 | Production traffic shall use HTTPS, hashed passwords, short-lived JWTs, parameterized queries, and environment-managed secrets. |
| NFR-004 | Pydantic shall validate all API and imported data. |
| NFR-005 | Multi-record writes/imports shall use database transactions and safe rollback. |
| NFR-006 | MySQL shall have daily backups and version-controlled Alembic migrations. |
| NFR-007 | The UI shall show clear loading, validation, empty, success, and failure states. |
| NFR-008 | Core services and endpoints shall have unit/integration tests. |
| NFR-009 | The services shall be runnable in a local Python environment with a local MySQL 8 service. |

## 5. Acceptance criteria

The release is acceptable when valid traffic data is stored and classified correctly; qualifying traffic conditions create manageable alerts; incidents are tracked; authorized users see only permitted data; dashboard figures/charts match filtered records; CSV exports match displayed scope; audit entries record critical actions; and migration, API, and essential workflow tests pass.
