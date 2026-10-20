
import os
import uuid

from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage for this first prototype.
records = {}

# Internal services must present this shared secret.
SERVICE_TOKEN = os.environ.get("RESOURCE_SERVICE_TOKEN")

if not SERVICE_TOKEN:
    raise RuntimeError(
        "Set the RESOURCE_SERVICE_TOKEN environment variable."
    )


def internal_request_is_valid():
    """Check whether the caller has the internal service token."""
    supplied_token = request.headers.get("X-Service-Token", "")
    return supplied_token == SERVICE_TOKEN


def get_user_context():
    """Read the user identity and role asserted by the trusted API."""
    user_id = request.headers.get("X-User-Id")
    role = request.headers.get("X-User-Role")

    if not user_id or role not in {"user", "admin"}:
        return None

    return {"user_id": user_id, "role": role}


def require_internal_request():
    """Reject requests that do not come from an authorized service."""
    if not internal_request_is_valid():
        return jsonify({"error": "Unauthorized service"}), 401

    return None


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/internal/records")
def create_record():
    denied = require_internal_request()
    if denied:
        return denied

    context = get_user_context()
    if context is None:
        return jsonify({"error": "Invalid user context"}), 401

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    title = data.get("title")
    content = data.get("content")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "A non-empty title is required"}), 400

    if not isinstance(content, str) or not content.strip():
        return jsonify({"error": "Non-empty content is required"}), 400

    if len(title) > 200 or len(content) > 10000:
        return jsonify({"error": "Input exceeds the allowed size"}), 400

    record_id = str(uuid.uuid4())

    record = {
    "id": record_id,
    "owner_id": data.get("owner_id", context["user_id"]),
    "title": title.strip(),
    "content": content.strip(),
}

    records[record_id] = record

    return jsonify({"record": record}), 201


@app.get("/internal/records")
def list_records():
    denied = require_internal_request()
    if denied:
        return denied

    context = get_user_context()
    if context is None:
        return jsonify({"error": "Invalid user context"}), 401

    if context["role"] == "admin":
        return jsonify({"error": "Operation not permitted"}), 403

    owned_records = [
        record
        for record in records.values()
        if record["owner_id"] == context["user_id"]
    ]

    return jsonify({"records": owned_records}), 200


@app.get("/internal/records/<record_id>")
def get_record(record_id):
    denied = require_internal_request()
    if denied:
        return denied

    context = get_user_context()
    if context is None:
        return jsonify({"error": "Invalid user context"}), 401

    record = records.get(record_id)
    if record is None:
        return jsonify({"error": "Record not found"}), 404

    # INTENTIONAL VULNERABILITY:
    # The service does not check whether the requesting user owns the record.
    return jsonify({"record": record}), 200


@app.get("/internal/admin/stats")
def admin_stats():
    denied = require_internal_request()
    if denied:
        return denied

    context = get_user_context()
    if context is None:
        return jsonify({"error": "Invalid user context"}), 401

    if context["role"] != "admin":
        return jsonify({"error": "Forbidden"}), 403

    return jsonify({
        "record_count": len(records),
        "unique_owner_count": len({
            record["owner_id"] for record in records.values()
        }),
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
