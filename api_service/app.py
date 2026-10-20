
import os
import secrets
import requests

from flask import Flask, jsonify, request

app = Flask(__name__)

# Demo users for local development.
# We will improve credential handling and authentication later.
USERS = {
    "alice": {"password": "alice-demo-123", "role": "user"},
    "bob": {"password": "bob-demo-123", "role": "user"},
    "admin": {"password": "admin-demo-123", "role": "admin"},
}

# Keep track of tokens issued by this API process.
# Each token maps to the user who logged in.
active_tokens = {}

RESOURCE_SERVICE_URL = "http://127.0.0.1:5001"
PROCESSING_SERVICE_URL = "http://127.0.0.1:5002"

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

    user = USERS.get(username)

    if user is None or not secrets.compare_digest(
        password, user["password"]
    ):
        return jsonify({"error": "Invalid username or password"}), 401

    token = secrets.token_urlsafe(32)
    active_tokens[token] = {
        "user_id": username,
        "role": user["role"],
    }

    return jsonify({
        "token": token,
        "user_id": username,
        "role": user["role"],
    }), 200


def get_current_user():
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
            headers={
                "X-Service-Token": os.environ.get(
                    "RESOURCE_SERVICE_TOKEN",
                    "local-dev-secret-change-me",
                ),
                "X-User-Id": user["user_id"],
                "X-User-Role": user["role"],
            },
            json=data,
            timeout=5,
        )
    except requests.RequestException:
        return jsonify({"error": "Resource Service unavailable"}), 502

    return jsonify(response.json()), response.status_code



@app.post("/records/<record_id>/process")
def process_record(record_id):
    user = get_current_user()

    if user is None:
        return jsonify({"error": "Authentication required"}), 401

    try:
        # Ask the Resource Service for this user's record.
        record_response = requests.get(
            f"{RESOURCE_SERVICE_URL}/internal/records/{record_id}",
            headers={
                "X-Service-Token": os.environ.get(
                    "RESOURCE_SERVICE_TOKEN",
                    "local-dev-secret-change-me",
                ),
                "X-User-Id": user["user_id"],
                "X-User-Role": user["role"],
            },
            timeout=5,
        )

        if record_response.status_code != 200:
            return jsonify(record_response.json()), record_response.status_code

        record = record_response.json()["record"]

        # Send the record's content to the Processing Service.
        processing_response = requests.post(
            f"{PROCESSING_SERVICE_URL}/internal/process",
            headers={
                "X-Service-Token": os.environ.get(
                    "PROCESSING_SERVICE_TOKEN",
                    "processing-local-secret-change-me",
                ),
            },
            json={"text": record["content"]},
            timeout=5,
        )

        return jsonify(processing_response.json()), processing_response.status_code

    except requests.RequestException:
        return jsonify({"error": "A dependent service is unavailable"}), 502



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
