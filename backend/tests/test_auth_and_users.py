"""
SENTRA – Authentication and User Management Test Suite
Validates Phase 7 and Phase 8 implementations:
1. User registration
2. Duplicate email handling
3. Invalid input validation
4. User login & JWT issuance
5. Invalid credentials rejection
6. Profile retrieval & password_hash protection
7. Profile updates & role immutability
8. Secure password changes and re-authentication
9. Stateless logout
10. RBAC (USER vs ADMIN) dependency enforcement
"""

import pytest
from app.models.user import User
from app.core.security import hash_password
from app.core.dependencies import get_current_admin_user


# ------------------------------------------------------------------------------
# 1-4: Registration Tests
# ------------------------------------------------------------------------------

def test_register_new_user_success(client):
    """1. Test successful user registration."""
    payload = {
        "name": "Jane Safe",
        "email": "jane.safe@example.com",
        "phone": "9876543210",
        "password": "SecurePassword123"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane Safe"
    assert data["email"] == "jane.safe@example.com"
    assert data["phone"] == "9876543210"
    assert data["role"] == "user"
    assert "user_id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email(client):
    """2. Test registration rejection on duplicate email (409 Conflict)."""
    payload = {
        "name": "First User",
        "email": "duplicate@example.com",
        "password": "Password123"
    }
    res1 = client.post("/api/auth/register", json=payload)
    assert res1.status_code == 201

    # Attempt second registration with same email
    res2 = client.post("/api/auth/register", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()


def test_register_invalid_input_validation(client):
    """3 & 4. Test validation failure on missing fields or short passwords (422)."""
    # Missing email & name
    res1 = client.post("/api/auth/register", json={"password": "short"})
    assert res1.status_code == 422

    # Password shorter than minimum required length (6 chars)
    res2 = client.post("/api/auth/register", json={
        "name": "Test",
        "email": "valid@example.com",
        "password": "123"
    })
    assert res2.status_code == 422


# ------------------------------------------------------------------------------
# 5-7: Login Tests
# ------------------------------------------------------------------------------

def test_login_correct_credentials(client):
    """5. Test login with correct credentials returns valid JWT token."""
    # Register user first
    client.post("/api/auth/register", json={
        "name": "John Login",
        "email": "john@example.com",
        "password": "MySecretPassword"
    })

    # Login
    response = client.post("/api/auth/login", json={
        "email": "john@example.com",
        "password": "MySecretPassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


def test_login_wrong_password(client):
    """6. Test login rejection with wrong password (401)."""
    client.post("/api/auth/register", json={
        "name": "Wrong Pass User",
        "email": "wrongpass@example.com",
        "password": "CorrectPassword"
    })

    response = client.post("/api/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "IncorrectPassword"
    })
    assert response.status_code == 401
    assert "invalid email or password" in response.json()["detail"].lower()


def test_login_non_existing_email(client):
    """7. Test login rejection with non-existing email (401)."""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "SomePassword"
    })
    assert response.status_code == 401


# ------------------------------------------------------------------------------
# 8-10: Profile Access & Token Verification
# ------------------------------------------------------------------------------

def test_access_profile_without_token(client):
    """8. Test profile access rejection without token (401)."""
    response = client.get("/api/users/profile")
    assert response.status_code == 401


def test_access_profile_with_valid_token(client):
    """9. Test profile access with valid JWT token."""
    client.post("/api/auth/register", json={
        "name": "Token User",
        "email": "tokenuser@example.com",
        "phone": "5551234",
        "password": "ValidPassword"
    })
    login_res = client.post("/api/auth/login", json={
        "email": "tokenuser@example.com",
        "password": "ValidPassword"
    })
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/users/profile",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Token User"
    assert data["email"] == "tokenuser@example.com"
    assert data["phone"] == "5551234"
    assert data["role"] == "user"
    assert "password" not in data
    assert "password_hash" not in data


def test_access_profile_with_invalid_token(client):
    """10. Test profile access rejection with invalid token (401)."""
    response = client.get(
        "/api/users/profile",
        headers={"Authorization": "Bearer invalid_garbage_token"}
    )
    assert response.status_code == 401


# ------------------------------------------------------------------------------
# 11-12: Profile Updates & Role Immutability
# ------------------------------------------------------------------------------

def test_update_own_profile(client):
    """11. Test updating allowed profile fields."""
    client.post("/api/auth/register", json={
        "name": "Original Name",
        "email": "update@example.com",
        "phone": "1111111",
        "password": "Password123"
    })
    token = client.post("/api/auth/login", json={
        "email": "update@example.com",
        "password": "Password123"
    }).json()["access_token"]

    # Update name and phone
    response = client.put(
        "/api/users/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Updated Name", "phone": "9999999"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["phone"] == "9999999"
    assert data["email"] == "update@example.com"


def test_unauthorized_role_modification_attempt(client):
    """12. Test that users cannot escalate their role via profile update."""
    client.post("/api/auth/register", json={
        "name": "Standard User",
        "email": "norolechange@example.com",
        "password": "Password123"
    })
    token = client.post("/api/auth/login", json={
        "email": "norolechange@example.com",
        "password": "Password123"
    }).json()["access_token"]

    # Attempt to send role in payload
    response = client.put(
        "/api/users/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New Name", "role": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "user"  # Role remains strictly 'user'


# ------------------------------------------------------------------------------
# 13-15: Password Change & Re-Authentication
# ------------------------------------------------------------------------------

def test_change_password_success_and_login_with_new_password(client):
    """13 & 15. Test changing password with correct credentials and logging in."""
    client.post("/api/auth/register", json={
        "name": "Pass Change User",
        "email": "passchange@example.com",
        "password": "OldPassword123"
    })
    token = client.post("/api/auth/login", json={
        "email": "passchange@example.com",
        "password": "OldPassword123"
    }).json()["access_token"]

    # Change password
    change_res = client.put(
        "/api/users/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "OldPassword123",
            "new_password": "NewSecretPassword456"
        }
    )
    assert change_res.status_code == 200
    assert "successfully" in change_res.json()["message"].lower()

    # Old password should now fail
    old_login = client.post("/api/auth/login", json={
        "email": "passchange@example.com",
        "password": "OldPassword123"
    })
    assert old_login.status_code == 401

    # New password should succeed
    new_login = client.post("/api/auth/login", json={
        "email": "passchange@example.com",
        "password": "NewSecretPassword456"
    })
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()


def test_change_password_wrong_current_password(client):
    """14. Test password change rejection with incorrect current password."""
    client.post("/api/auth/register", json={
        "name": "User",
        "email": "wrongcurrent@example.com",
        "password": "ActualPassword"
    })
    token = client.post("/api/auth/login", json={
        "email": "wrongcurrent@example.com",
        "password": "ActualPassword"
    }).json()["access_token"]

    response = client.put(
        "/api/users/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "IncorrectPassword",
            "new_password": "NewPassword123"
        }
    )
    assert response.status_code == 400
    assert "incorrect current password" in response.json()["detail"].lower()


# ------------------------------------------------------------------------------
# 16-18: Security, Role-Based Access Control, and Logout
# ------------------------------------------------------------------------------

def test_password_hash_never_exposed(client):
    """16. Verify password_hash is never exposed in registration, profile, or login."""
    reg = client.post("/api/auth/register", json={
        "name": "Sec Test",
        "email": "sectest@example.com",
        "password": "MyPassword123"
    })
    assert "password_hash" not in reg.text

    login = client.post("/api/auth/login", json={
        "email": "sectest@example.com",
        "password": "MyPassword123"
    })
    assert "password_hash" not in login.text

    token = login.json()["access_token"]
    profile = client.get("/api/users/profile", headers={"Authorization": f"Bearer {token}"})
    assert "password_hash" not in profile.text


def test_rbac_user_cannot_access_admin_dependency(db_session):
    """17 & 18. Verify USER cannot access admin dependency while ADMIN can."""
    # 1. Standard user
    user = User(
        name="Regular User",
        email="regular@example.com",
        password_hash=hash_password("Password123"),
        role="user"
    )
    db_session.add(user)
    db_session.commit()

    with pytest.raises(Exception) as exc_info:
        import asyncio
        asyncio.run(get_current_admin_user(current_user=user))
    assert "administrator privileges required" in str(exc_info.value).lower()

    # 2. Admin user
    admin_user = User(
        name="Chief Admin",
        email="chief.admin@sentra.local",
        password_hash=hash_password("AdminPass123"),
        role="admin"
    )
    db_session.add(admin_user)
    db_session.commit()

    import asyncio
    verified_admin = asyncio.run(get_current_admin_user(current_user=admin_user))
    assert verified_admin.role == "admin"


def test_logout_endpoint(client):
    """Test POST /api/auth/logout with authenticated token."""
    client.post("/api/auth/register", json={
        "name": "Logout User",
        "email": "logout@example.com",
        "password": "Password123"
    })
    token = client.post("/api/auth/login", json={
        "email": "logout@example.com",
        "password": "Password123"
    }).json()["access_token"]

    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "successfully logged out" in response.json()["message"].lower()
