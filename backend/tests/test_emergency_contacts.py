"""
SENTRA – Emergency Contacts Management Test Suite (Phase 9)
Validates the complete Emergency Contacts CRUD, authentication enforcement,
data isolation (ownership), input validation, and error handling.

Tests:
1.  Create emergency contact (POST /api/users/emergency-contacts)
2.  Create via alias route (POST /api/emergency-contacts)
3.  Invalid input validation (missing name, bad phone)
4.  List all contacts – data isolation between users
5.  Get contact by ID
6.  Update contact fields
7.  Delete contact and verify removal
8.  Unauthenticated access rejected (401) for all verbs
9.  Ownership enforcement – cannot access/modify another user's contact (404)
10. Non-existent contact ID returns 404
"""

import pytest


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def register_and_login(client, name: str, email: str, password: str = "Password123") -> str:
    """Register a user and return their JWT access token."""
    client.post("/api/auth/register", json={"name": name, "email": email, "password": password})
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


# ---------------------------------------------------------------------------
# 1. Create Emergency Contact
# ---------------------------------------------------------------------------

def test_create_emergency_contact_success(client):
    """POST /api/users/emergency-contacts – successful creation."""
    token = register_and_login(client, "Alice", "alice@example.com")
    response = client.post(
        "/api/users/emergency-contacts",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_name": "Bob Smith", "phone": "+1 555 123 4567", "relationship": "Brother"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["contact_name"] == "Bob Smith"
    assert data["phone"] == "+1 555 123 4567"
    assert data["relationship"] == "Brother"
    assert "contact_id" in data
    assert "user_id" in data
    assert "password_hash" not in response.text


def test_create_emergency_contact_alias_route(client):
    """POST /api/emergency-contacts alias route also works."""
    token = register_and_login(client, "Charlie", "charlie@example.com")
    response = client.post(
        "/api/emergency-contacts",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_name": "David", "phone": "9876543210", "relationship": "Father"},
    )
    assert response.status_code == 201
    assert response.json()["contact_name"] == "David"


# ---------------------------------------------------------------------------
# 2. Input Validation
# ---------------------------------------------------------------------------

def test_create_contact_missing_name(client):
    """422 when contact_name is missing."""
    token = register_and_login(client, "Dana", "dana@example.com")
    res = client.post(
        "/api/users/emergency-contacts",
        headers={"Authorization": f"Bearer {token}"},
        json={"phone": "1234567890"},
    )
    assert res.status_code == 422


def test_create_contact_invalid_phone_format(client):
    """422 when phone contains letters or invalid characters."""
    token = register_and_login(client, "Ethan", "ethan@example.com")
    res = client.post(
        "/api/users/emergency-contacts",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_name": "Test Person", "phone": "not-a-phone-number!!"},
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 3. List Contacts – Data Isolation
# ---------------------------------------------------------------------------

def test_get_all_contacts_data_isolation(client):
    """Each user sees only their own contacts."""
    token1 = register_and_login(client, "User One", "user1@example.com")
    token2 = register_and_login(client, "User Two", "user2@example.com")

    # User 1 creates 2 contacts
    for payload in [
        {"contact_name": "Mom", "phone": "1111111111", "relationship": "Mother"},
        {"contact_name": "Dad", "phone": "2222222222", "relationship": "Father"},
    ]:
        client.post("/api/users/emergency-contacts",
                    headers={"Authorization": f"Bearer {token1}"}, json=payload)

    # User 2 creates 1 contact
    client.post("/api/users/emergency-contacts",
                headers={"Authorization": f"Bearer {token2}"},
                json={"contact_name": "Sister", "phone": "3333333333", "relationship": "Sister"})

    res1 = client.get("/api/users/emergency-contacts",
                      headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == 200
    names1 = [c["contact_name"] for c in res1.json()]
    assert "Mom" in names1 and "Dad" in names1
    assert "Sister" not in names1
    assert len(names1) == 2

    res2 = client.get("/api/users/emergency-contacts",
                      headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == 200
    assert len(res2.json()) == 1
    assert res2.json()[0]["contact_name"] == "Sister"


# ---------------------------------------------------------------------------
# 4. Get Contact by ID
# ---------------------------------------------------------------------------

def test_get_contact_by_id_success(client):
    """GET /api/users/emergency-contacts/{id} returns the correct contact."""
    token = register_and_login(client, "Eve", "eve@example.com")
    create_res = client.post(
        "/api/users/emergency-contacts",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_name": "Dr. House", "phone": "5559876", "relationship": "Doctor"},
    )
    contact_id = create_res.json()["contact_id"]

    res = client.get(
        f"/api/users/emergency-contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["contact_id"] == contact_id
    assert res.json()["contact_name"] == "Dr. House"


# ---------------------------------------------------------------------------
# 5. Update Contact
# ---------------------------------------------------------------------------

def test_update_emergency_contact(client):
    """PUT updates permitted contact fields."""
    token = register_and_login(client, "Frank", "frank@example.com")
    create_res = client.post(
        "/api/users/emergency-contacts",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_name": "Original Name", "phone": "5550000", "relationship": "Friend"},
    )
    contact_id = create_res.json()["contact_id"]

    update_res = client.put(
        f"/api/users/emergency-contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_name": "Updated Name", "phone": "+1 555 999 8888", "relationship": "Best Friend"},
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["contact_name"] == "Updated Name"
    assert data["phone"] == "+1 555 999 8888"
    assert data["relationship"] == "Best Friend"


# ---------------------------------------------------------------------------
# 6. Delete Contact
# ---------------------------------------------------------------------------

def test_delete_emergency_contact(client):
    """DELETE removes contact and subsequent GET returns 404."""
    token = register_and_login(client, "Grace", "grace@example.com")
    create_res = client.post(
        "/api/users/emergency-contacts",
        headers={"Authorization": f"Bearer {token}"},
        json={"contact_name": "Temp Contact", "phone": "5551122"},
    )
    contact_id = create_res.json()["contact_id"]

    del_res = client.delete(
        f"/api/users/emergency-contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert del_res.status_code == 200
    assert "deleted successfully" in del_res.json()["message"].lower()
    assert del_res.json()["contact_id"] == contact_id

    # Confirm deletion
    get_res = client.get(
        f"/api/users/emergency-contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_res.status_code == 404


# ---------------------------------------------------------------------------
# 7. Unauthenticated Access
# ---------------------------------------------------------------------------

def test_unauthenticated_access_rejected(client):
    """All endpoints return 401 when no token is provided."""
    assert client.get("/api/users/emergency-contacts").status_code == 401
    assert client.post("/api/users/emergency-contacts",
                       json={"contact_name": "A", "phone": "123"}).status_code == 401
    assert client.get("/api/users/emergency-contacts/1").status_code == 401
    assert client.put("/api/users/emergency-contacts/1",
                      json={"contact_name": "A"}).status_code == 401
    assert client.delete("/api/users/emergency-contacts/1").status_code == 401


# ---------------------------------------------------------------------------
# 8. Ownership Enforcement
# ---------------------------------------------------------------------------

def test_ownership_enforcement(client):
    """Another authenticated user cannot read, update, or delete a contact they don't own."""
    token_victim = register_and_login(client, "Victim", "victim@example.com")
    token_attacker = register_and_login(client, "Attacker", "attacker@example.com")

    # Victim creates a contact
    res = client.post(
        "/api/users/emergency-contacts",
        headers={"Authorization": f"Bearer {token_victim}"},
        json={"contact_name": "Victim's Lawyer", "phone": "5559999", "relationship": "Attorney"},
    )
    contact_id = res.json()["contact_id"]

    # Attacker attempts GET -> 404
    assert client.get(
        f"/api/users/emergency-contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token_attacker}"},
    ).status_code == 404

    # Attacker attempts PUT -> 404
    assert client.put(
        f"/api/users/emergency-contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token_attacker}"},
        json={"contact_name": "Hacked"},
    ).status_code == 404

    # Attacker attempts DELETE -> 404
    assert client.delete(
        f"/api/users/emergency-contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token_attacker}"},
    ).status_code == 404

    # Victim's contact is unchanged
    check = client.get(
        f"/api/users/emergency-contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token_victim}"},
    )
    assert check.status_code == 200
    assert check.json()["contact_name"] == "Victim's Lawyer"


# ---------------------------------------------------------------------------
# 9. Non-Existent Contact
# ---------------------------------------------------------------------------

def test_nonexistent_contact_returns_404(client):
    """GET, PUT, DELETE on a non-existent ID all return 404."""
    token = register_and_login(client, "Harry", "harry@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/users/emergency-contacts/99999", headers=headers).status_code == 404
    assert client.put("/api/users/emergency-contacts/99999",
                      headers=headers, json={"contact_name": "New"}).status_code == 404
    assert client.delete("/api/users/emergency-contacts/99999", headers=headers).status_code == 404
