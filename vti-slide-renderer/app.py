# app.py — Flask entry point
from __future__ import annotations

import json
from pathlib import Path
from xml.etree import ElementTree as ET

from flask import Flask, jsonify, request, Response, render_template

from renderer.engine import render_deck, ValidationError
from renderer.design_system import resolve_deck

app = Flask(__name__)

_SCHEMA_PATH = Path(__file__).parent / "schemas" / "slide_deck.json"


def load_schema() -> dict:
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


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


@app.route("/generate", methods=["POST"])
def generate():
    """
    Accept a user text request, call Gemini to design the deck, resolve
    the design system, render to PPTX, and return the file for download.

    Body (JSON):
      { "request": "...", "theme": "VTI", "lang": "vi" }
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    body = request.get_json(silent=True) or {}
    user_request = body.get("request", "").strip()
    if not user_request:
        return jsonify({"error": "Missing 'request' field"}), 400

    theme = body.get("theme", "VTI")
    lang  = body.get("lang", "vi")

    try:
        from vertex_AI.slide_designer import SlideDesigner
        designer = SlideDesigner.from_config()
        intent_deck = designer.generate(user_request, theme=theme, lang=lang)
    except Exception as e:
        app.logger.exception("Gemini design error")
        return jsonify({"error": f"Design generation failed: {e}"}), 500

    try:
        pptx_bytes = render_deck(intent_deck)
    except ValidationError as e:
        return jsonify({"errors": e.errors}), 400
    except Exception as e:
        app.logger.exception("Render error")
        return jsonify({"error": str(e)}), 500

    title = intent_deck.get("deck_meta", {}).get("title", "presentation")
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title).strip()
    filename = f"{safe_title or 'presentation'}.pptx"

    return Response(
        pptx_bytes,
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@app.route("/design-intent", methods=["POST"])
def design_intent():
    """
    Like /generate but returns the resolved design JSON instead of a PPTX file.
    Useful for debugging the Gemini output and design resolution.

    Body (JSON):
      { "request": "...", "theme": "VTI", "lang": "vi" }
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    body = request.get_json(silent=True) or {}
    user_request = body.get("request", "").strip()
    if not user_request:
        return jsonify({"error": "Missing 'request' field"}), 400

    theme = body.get("theme", "VTI")
    lang  = body.get("lang", "vi")

    try:
        from vertex_AI.slide_designer import SlideDesigner
        designer = SlideDesigner.from_config()
        intent_deck = designer.generate(user_request, theme=theme, lang=lang)
    except Exception as e:
        app.logger.exception("Gemini design error")
        return jsonify({"error": f"Design generation failed: {e}"}), 500

    resolved = resolve_deck(intent_deck)
    return jsonify({"intent": intent_deck, "resolved": resolved})


@app.route("/svg-to-pptx", methods=["POST"])
def svg_to_pptx():
    """
    Convert one or more SVG strings to a single .pptx file.
    Each SVG becomes one slide.

    Body (JSON):
      {
        "title": "Deck title",          // optional, default "presentation"
        "slides": ["<svg>...</svg>", …] // required, min 1 element
      }
    """
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    body = request.get_json(silent=True) or {}
    slides_svg: list = body.get("slides", [])
    if not slides_svg or not isinstance(slides_svg, list):
        return jsonify({"error": "'slides' must be a non-empty list of SVG strings"}), 400

    title = body.get("title", "presentation")

    try:
        from renderer.svg_parser import parse_svg_to_slide
        from pptx import Presentation
        from pptx.util import Emu
        from renderer import geometry as G
        import io

        prs = Presentation()
        prs.slide_width  = Emu(G.SLIDE_W)
        prs.slide_height = Emu(G.SLIDE_H)

        for svg_str in slides_svg:
            if not isinstance(svg_str, str) or not svg_str.strip():
                return jsonify({"error": "Each slide must be a non-empty SVG string"}), 400
            parse_svg_to_slide(prs, svg_str)

        buf = io.BytesIO()
        prs.save(buf)
        pptx_bytes = buf.getvalue()

    except ET.ParseError as e:
        return jsonify({"error": f"SVG parse error: {e}"}), 400
    except Exception as e:
        app.logger.exception("SVG render error")
        return jsonify({"error": str(e)}), 500

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
    app.run(debug=True, host="127.0.0.1", port=5020)
