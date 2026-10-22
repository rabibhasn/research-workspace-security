
import os
import secrets
import hmac
import hashlib
import json

import requests
from flask import Flask, jsonify, request

if __package__:
    from .database import (
        get_user_by_username,
        initialize_database,
        verify_password,
    )
else:
    from database import (
        get_user_by_username,
        initialize_database,
        verify_password,
    )

app = Flask(__name__)

# In-memory login tokens for this coursework prototype.
active_tokens = {}

RESOURCE_SERVICE_URL = "http://127.0.0.1:5001"
PROCESSING_SERVICE_URL = "http://127.0.0.1:5002"


def get_required_secret(name):
    """Read a required secret without a hardcoded fallback."""
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Set the {name} environment variable.")
    return value


def sign_user_context(user):
    """Sign the authenticated user's ID and role."""
    secret = get_required_secret("USER_CONTEXT_SECRET")

    context_data = json.dumps(
        {
            "user_id": user["user_id"],
            "role": user["role"],
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return hmac.new(
        secret.encode("utf-8"),
        context_data,
        hashlib.sha256,
    ).hexdigest()


def resource_service_headers(user):
    """Build authenticated headers for Resource Service requests."""
    return {
        "X-Service-Token": get_required_secret(
            "RESOURCE_SERVICE_TOKEN"
        ),
        "X-User-Id": user["user_id"],
        "X-User-Role": user["role"],
        "X-User-Context-Signature": sign_user_context(user),
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/login")
def login():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    username = data.get("username")
    password = data.get("password")

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid username or password"}), 401

    user = get_user_by_username(username)

    if user is None or not verify_password(
        password,
        user["password_salt"],
        user["password_hash"],
    ):
        return jsonify({"error": "Invalid username or password"}), 401

    token = secrets.token_urlsafe(32)

    active_tokens[token] = {
        "user_id": user["username"],
        "role": user["role"],
    }

    return jsonify({
        "token": token,
        "user_id": user["username"],
        "role": user["role"],
    }), 200


def get_current_user():
    """Resolve a bearer token to its authenticated user."""
    authorization = request.headers.get("Authorization", "")
    scheme, separator, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not separator or not token:
        return None

    return active_tokens.get(token)


@app.post("/records")
def create_record():
    user = get_current_user()

    if user is None:
        return jsonify({"error": "Authentication required"}), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    try:
        response = requests.post(
            f"{RESOURCE_SERVICE_URL}/internal/records",
            headers=resource_service_headers(user),
            json=data,
            timeout=5,
        )
    except RuntimeError:
        app.logger.exception("Service configuration is missing")
        return jsonify({"error": "Service configuration error"}), 500
    except requests.RequestException:
        return jsonify({"error": "Resource Service unavailable"}), 502

    try:
        return jsonify(response.json()), response.status_code
    except requests.exceptions.JSONDecodeError:
        return jsonify({
            "error": "Invalid response from Resource Service"
        }), 502


@app.post("/records/<record_id>/process")
def process_record(record_id):
    user = get_current_user()

    if user is None:
        return jsonify({"error": "Authentication required"}), 401

    try:
        # Verify that this user may access the requested record.
        record_response = requests.get(
            f"{RESOURCE_SERVICE_URL}/internal/records/{record_id}",
            headers=resource_service_headers(user),
            timeout=5,
        )

        if record_response.status_code != 200:
            try:
                return (
                    jsonify(record_response.json()),
                    record_response.status_code,
                )
            except requests.exceptions.JSONDecodeError:
                return jsonify({
                    "error": "Invalid response from Resource Service"
                }), 502

        record = record_response.json()["record"]

        # Process content only after the access check succeeds.
        processing_response = requests.post(
            f"{PROCESSING_SERVICE_URL}/internal/process",
            headers={
                "X-Service-Token": get_required_secret(
                    "PROCESSING_SERVICE_TOKEN"
                ),
            },
            json={"text": record["content"]},
            timeout=5,
        )

        try:
            return (
                jsonify(processing_response.json()),
                processing_response.status_code,
            )
        except requests.exceptions.JSONDecodeError:
            return jsonify({
                "error": "Invalid response from Processing Service"
            }), 502

    except RuntimeError:
        app.logger.exception("Service configuration is missing")
        return jsonify({"error": "Service configuration error"}), 500
    except (requests.RequestException, KeyError):
        return jsonify({
            "error": "A dependent service is unavailable"
        }), 502


# Ensure the SQLite users table exists when the API module is loaded.
initialize_database()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
