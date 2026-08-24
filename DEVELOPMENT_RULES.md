# SENTRA – Development Rules

## 1. Purpose

These rules maintain consistency, security, quality, and maintainability throughout SENTRA development.

## 2. General Rules

- Keep code modular.
- Use meaningful names.
- Avoid duplicate logic.
- Keep functions focused.
- Document important business logic.
- Validate all external input.
- Never commit secrets.

## 3. Python Rules

Follow PEP 8.

Use `snake_case` for variables and functions and `PascalCase` for classes.

```python
def create_event():
    pass

class EventService:
    pass
```

## 4. FastAPI Rules

- Organize routes by module.
- Use Pydantic schemas for request validation.
- Separate routes from business logic.
- Use dependency injection for authentication and database sessions.
- Return consistent response structures.
- Handle exceptions safely.

## 5. Database Rules

- Use parameterized queries or an ORM.
- Never build SQL using unsafe string concatenation.
- Use foreign keys for relationships.
- Add indexes to frequently queried fields.
- Keep database credentials in environment variables.
- Perform backups regularly.

## 6. Authentication Rules

- Never store plain-text passwords.
- Use strong password hashing.
- Protect private endpoints.
- Implement role-based authorization.
- Do not expose tokens in logs.

## 7. Security Rules

- Validate every user-controlled value.
- Protect sensitive information.
- Use HTTPS in production.
- Configure CORS carefully.
- Do not commit `.env` files.
- Keep dependencies updated.
- Log security-relevant actions without exposing secrets.

## 8. Frontend Rules

- Use reusable components.
- Keep UI responsive.
- Display clear error messages.
- Do not store sensitive secrets in frontend code.
- Validate forms before submission while also validating on the backend.

## 9. Git Rules

Use meaningful branch names:

```text
feature/sos-module
feature/threat-detection
feature/admin-dashboard
fix/login-error
```

Commit messages should be clear:

```text
feat: add SOS event API
fix: resolve alert status validation
docs: update database schema
```

Do not commit:

```text
.env
__pycache__/
.venv/
node_modules/
*.log
```

## 10. Testing Rules

Test:

- Authentication
- User APIs
- SOS
- Event creation
- Threat detection
- Alert generation
- Admin authorization
- Database operations

Use unit, integration, and API tests where appropriate.

## 11. Error Handling

- Return useful HTTP status codes.
- Do not expose internal stack traces to users.
- Log technical details securely.
- Provide user-friendly error messages.

## 12. Code Review

Before merging code:

- Check functionality.
- Check security.
- Check naming.
- Check tests.
- Check documentation.
- Remove debug statements.
- Verify no secrets are included.

## 13. Documentation Rules

Update relevant Markdown documentation whenever:

- APIs change.
- Database schema changes.
- Architecture changes.
- New modules are added.
- Setup instructions change.

## 14. Definition of Done

A feature is complete when:

- Code is implemented.
- Tests pass.
- API behavior is verified.
- Security checks are completed.
- Documentation is updated.
- Code is reviewed.
- No known critical errors remain.
