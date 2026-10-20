
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

        assert response.status_code == 404
        assert response.get_json()["error"] == "Record not found"


def test_request_without_service_token_is_rejected():
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
