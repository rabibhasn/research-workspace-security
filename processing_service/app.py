
import os

from flask import Flask, jsonify, request
from research_helper import process_research_text

app = Flask(__name__)

SERVICE_TOKEN = os.environ.get("PROCESSING_SERVICE_TOKEN")

if not SERVICE_TOKEN:
    raise RuntimeError(
        "Set the PROCESSING_SERVICE_TOKEN environment variable."
    )


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/internal/process")
def process_text():
    supplied_token = request.headers.get("X-Service-Token", "")

    if supplied_token != SERVICE_TOKEN:
        return jsonify({"error": "Unauthorized service"}), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    text = data.get("text")

    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Non-empty text is required"}), 400

    if len(text) > 10000:
        return jsonify({"error": "Text exceeds the allowed size"}), 400

    result = process_research_text(text)

    return jsonify({"result": result}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=False)
