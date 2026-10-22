import os
import json
import hmac
import hashlib

os.environ["RESOURCE_SERVICE_TOKEN"] = "test-resource-token"
os.environ["USER_CONTEXT_SECRET"] = "test-user-context-secret"

from resource_service.app import app, records

SERVICE_HEADERS = {
    "X-Service-Token": "test-resource-token",
}

USER_CONTEXT_SECRET = "test-user-context-secret"


def user_headers(user_id, role="user"):
    context_data = json.dumps(
        {"user_id": user_id, "role": role},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    signature = hmac.new(
        USER_CONTEXT_SECRET.encode("utf-8"),
        context_data,
        hashlib.sha256,
    ).hexdigest()

    return {
        **SERVICE_HEADERS,
        "X-User-Id": user_id,
        "X-User-Role": role,
        "X-User-Context-Signature": signature,
    }


def test_user_can_access_own_record():
    """A user can create and read their own record."""
    records.clear()

    with app.test_client() as client:
        create_response = client.post(
            "/internal/records",
            headers=user_headers("alice"),
            json={
                "title": "Alice's research",
                "content": "Testing record ownership",
            },
        )

        assert create_response.status_code == 201
        record_id = create_response.get_json()["record"]["id"]

        response = client.get(
            f"/internal/records/{record_id}",
            headers=user_headers("alice"),
        )

        assert response.status_code == 200
        assert response.get_json()["record"]["owner_id"] == "alice"


def test_user_cannot_access_another_users_record():
    """Bob must not be able to read Alice's record."""
    records.clear()

    with app.test_client() as client:
        create_response = client.post(
            "/internal/records",
            headers=user_headers("alice"),
            json={
                "title": "Alice's private research",
                "content": "This belongs to Alice",
            },
        )

        assert create_response.status_code == 201
        record_id = create_response.get_json()["record"]["id"]

        response = client.get(
            f"/internal/records/{record_id}",
            headers=user_headers("bob"),
        )

        assert response.status_code == 403
        assert response.get_json()["error"] == "Forbidden"


def test_request_without_service_token_is_rejected():
    """Requests without the internal service token are rejected."""
    records.clear()

    with app.test_client() as client:
        response = client.get(
            "/internal/records",
            headers={
                "X-User-Id": "alice",
                "X-User-Role": "user",
            },
        )

        assert response.status_code == 401
        assert response.get_json()["error"] == "Unauthorized service"


def test_user_cannot_assign_record_to_another_owner():
    """The server must assign ownership from the user context."""
    records.clear()

    with app.test_client() as client:
        response = client.post(
            "/internal/records",
            headers=user_headers("alice"),
            json={
                "title": "Ownership test",
                "content": "Testing mass assignment",
                "owner_id": "bob",
            },
        )

        assert response.status_code == 201
        assert response.get_json()["record"]["owner_id"] == "alice"


def test_unsigned_caller_cannot_claim_admin_role():
    """An unsigned caller must not be able to claim the admin role."""
    with app.test_client() as client:
        response = client.get(
            "/internal/admin/stats",
            headers={
                "X-Service-Token": "test-resource-token",
                "X-User-Id": "alice",
                "X-User-Role": "admin",
            },
        )

    assert response.status_code == 401
