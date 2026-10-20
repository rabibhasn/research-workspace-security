
import os

# Set the token before importing the Flask application.
os.environ["RESOURCE_SERVICE_TOKEN"] = "test-resource-token"

from resource_service.app import app, records


SERVICE_HEADERS = {"X-Service-Token": "test-resource-token"}


def user_headers(user_id):
    return {
        **SERVICE_HEADERS,
        "X-User-Id": user_id,
        "X-User-Role": "user",
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


def test_vulnerability_user_can_access_another_users_record():
    """VULNERABILITY: Bob can read Alice's record."""
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

        # This is the insecure behavior expected on vulnerable main.
        assert response.status_code == 200
        assert response.get_json()["record"]["owner_id"] == "alice"


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


def test_vulnerability_user_can_assign_record_to_another_owner():
    """VULNERABILITY: Alice can assign a record to Bob."""
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
        assert response.get_json()["record"]["owner_id"] == "bob"


def test_vulnerability_internal_caller_can_claim_admin_role():
    """VULNERABILITY: The service trusts the caller-supplied role."""
    records.clear()

    with app.test_client() as client:
        response = client.get(
            "/internal/admin/stats",
            headers={
                "X-Service-Token": "test-resource-token",
                "X-User-Id": "alice",
                "X-User-Role": "admin",
            },
        )

        assert response.status_code == 200
        assert "record_count" in response.get_json()
