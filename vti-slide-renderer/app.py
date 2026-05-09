# app.py — Flask entry point
from __future__ import annotations

import json
from pathlib import Path

from flask import Flask, jsonify, request, Response

from renderer.engine import render_deck, ValidationError

app = Flask(__name__)

_SCHEMA_PATH = Path(__file__).parent / "schemas" / "slide_deck.json"


def load_schema() -> dict:
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


@app.route("/render", methods=["POST"])
def render():
    """
    Accept JSON body, return .pptx file for download.
    Content-Type must be application/json.
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    deck_json = request.get_json(silent=True)
    if deck_json is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        pptx_bytes = render_deck(deck_json)
    except ValidationError as e:
        return jsonify({"errors": e.errors}), 400
    except Exception as e:
        app.logger.exception("Render error")
        return jsonify({"error": str(e)}), 500

    title = deck_json.get("deck_meta", {}).get("title", "presentation")
    # Sanitize filename
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title).strip()
    filename = f"{safe_title or 'presentation'}.pptx"

    return Response(
        pptx_bytes,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})


@app.route("/schema", methods=["GET"])
def schema():
    """Return the JSON schema so Gemini can reference it."""
    return jsonify(load_schema())


if __name__ == "__main__":
    app.run(debug=True)
