# SENTRA – Database Schema

## 1. Database

Recommended database name:

```sql
sentra_db
```

Recommended DBMS:

```text
MySQL 8+
```

## 2. Users Table

```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(30) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. Emergency Contacts Table

```sql
CREATE TABLE emergency_contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    relationship VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 4. Events Table

```sql
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    description TEXT,
    status VARCHAR(30) DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 5. Alerts Table

```sql
CREATE TABLE alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL,
    status VARCHAR(30) DEFAULT 'new',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 6. Locations Table

```sql
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    latitude DECIMAL(10,7) NOT NULL,
    longitude DECIMAL(10,7) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 7. Audit Logs Table

```sql
CREATE TABLE audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 8. Relationships

```text
users 1 ---- N emergency_contacts
users 1 ---- N events
users 1 ---- N alerts
users 1 ---- N locations
users 1 ---- N audit_logs
events 1 --- N alerts
```

## 9. Risk Levels

```text
LOW
MEDIUM
HIGH
CRITICAL
```

## 10. Event Status

```text
new
acknowledged
investigating
resolved
```

## 11. Recommended Indexes

Indexes should be considered for:

- users.email
- events.user_id
- events.risk_level
- events.status
- events.created_at
- alerts.status
- alerts.priority

## 12. Data Integrity

- Use primary keys for unique records.
- Use foreign keys for relationships.
- Use NOT NULL for mandatory fields.
- Use UNIQUE constraints for unique identifiers.
- Validate application input before database insertion.
