# html_renderer.py — Playwright-based PNG renderer for visual slides
#
# Visual slides (Cover, Section Divider, CTA) are rendered via Chromium
# headless at 2× retina resolution then embedded as full-slide pictures.
# This gives pixel-perfect CSS gradients, shadows, and typography that
# python-pptx OOXML cannot fully replicate.
#
# Public API
# ----------
# VISUAL_LAYOUTS : set[str]   — layout keys handled here (not by LAYOUT_MAP)
# render_to_png(layout_key, slide_data) -> bytes   — returns PNG bytes
from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

# ── Paths ─────────────────────────────────────────────────────────────────────
_TEMPLATES_DIR = Path(__file__).parent / "html_templates"

_jinja_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)

# ── Slide viewport (matches geometry.py slide dimensions at 1pt = 1px) ───────
_VIEWPORT_W = 1280
_VIEWPORT_H = 720
_SCALE = 2          # device pixel ratio — output PNG is 2560 × 1440

# ── Layout registry ───────────────────────────────────────────────────────────
VISUAL_LAYOUTS: set[str] = {"I", "G", "H"}


# ─────────────────────────────────────────────────────────────────────────────
# Colour helpers
# ─────────────────────────────────────────────────────────────────────────────

def _css(hex6: str) -> str:
    """Convert 6-char hex (no #) to CSS #RRGGBB."""
    return f"#{hex6.lstrip('#').upper()}"


def _rgba(hex6: str, alpha_pct: int) -> str:
    """Convert 6-char hex + integer opacity 0-100 to CSS rgba(...)."""
    h = hex6.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha_pct / 100:.2f})"


def _linear(from_hex: str, to_hex: str, direction: str = "to bottom") -> str:
    """CSS linear-gradient shorthand."""
    return f"linear-gradient({direction}, {_css(from_hex)}, {_css(to_hex)})"


# ─────────────────────────────────────────────────────────────────────────────
# Context builders — extract design data and produce template-ready dicts
# ─────────────────────────────────────────────────────────────────────────────

def _cover_ctx(slide_data: dict) -> dict[str, Any]:
    d = slide_data.get("design", {})
    sn = slide_data.get("slide_number", 1)

    bg = d.get("bg", {"from": "FFFFFF", "to": "EEF4FB"})
    lb = d.get("left_bar", {"from": "172759", "to": "2362B0"})
    rs = d.get("right_strip", {"from": "2362B0", "to": "4A9EE0", "opacity": 30})
    rc = d.get("right_card", {})
    rc_bg = rc.get("bg", {"from": "EBF4FC", "to": "D6EAF8"})
    div = d.get("divider_bar", {"from": "2362B0", "to": "7FC236"})

    border_top = rc.get("border_top", "7FC236")

    return {
        "slide_number": sn,
        # Background
        "bg_gradient": _linear(bg["from"], bg["to"]),
        # Left vertical bar (top→bottom)
        "left_bar_gradient": _linear(lb["from"], lb["to"]),
        # Right decorative strip (left→right, semi-transparent)
        "right_strip_from": _rgba(rs["from"], rs.get("opacity", 30)),
        "right_strip_to":   _rgba(rs["to"],   rs.get("opacity", 30)),
        # Right card
        "rc_gradient": _linear(rc_bg["from"], rc_bg["to"], "to top"),
        "rc_border_top": _css(border_top),
        "rc_decor_color": _rgba(border_top, 7),
        # Divider bar
        "divider_gradient": _linear(div["from"], div["to"], "to right"),
        # Text
        "tag":            d.get("tag", ""),
        "tag_color":      _css(d.get("tag_color", "2362B0")),
        "title":          d.get("title", ""),
        "title_color":    _css(d.get("title_color", "172759")),
        "subtitle":       d.get("subtitle", ""),
        "subtitle_color": _css(d.get("subtitle_color", "172759")),
        "caption":        d.get("caption", ""),
        "caption_color":  _css(d.get("caption_color", "6A7FA0")),
    }


def _section_divider_ctx(slide_data: dict) -> dict[str, Any]:
    d = slide_data.get("design", {})
    sn = slide_data.get("slide_number", 1)

    bg = d.get("bg", {"from": "172759", "to": "1A3070"})
    lb = d.get("left_bar", {"from": "2362B0", "to": "7FC236"})
    decor = d.get("decor", {"color": "1A3070", "opacity": 20})
    rc = d.get("right_card", {})
    rc_bg = rc.get("bg", {"from": "EBF4FC", "to": "D6EAF8"})
    border_top = rc.get("border_top", "4A9EE0")

    return {
        "slide_number": sn,
        "bg_gradient":  _linear(bg["from"], bg["to"]),
        "left_bar_gradient": _linear(lb["from"], lb["to"]),
        # Decorative circle top-right
        "decor_color":  _rgba(decor["color"], decor.get("opacity", 20)),
        # Right card
        "rc_gradient":    _linear(rc_bg["from"], rc_bg["to"], "to top"),
        "rc_border_top":  _css(border_top),
        "rc_decor_color": _rgba(border_top, 7),
        # Text (left zone)
        "section_number":       d.get("section_number", ""),
        "section_number_color": _css(d.get("section_number_color", "6A7FA0")),
        "section_title":        d.get("section_title", ""),
        "section_title_color":  _css(d.get("section_title_color", "FFFFFF")),
        "subtitle":             d.get("subtitle", ""),
        "subtitle_color":       _css(d.get("subtitle_color", "B8D0EE")),
    }


def _cta_ctx(slide_data: dict) -> dict[str, Any]:
    d = slide_data.get("design", {})
    sn = slide_data.get("slide_number", 1)

    bg = d.get("bg", {"from": "2362B0", "to": "172759"})
    decor_color = d.get("decor_color", "2362B0")

    items = d.get("items", [])

    return {
        "slide_number": sn,
        "bg_gradient":      _linear(bg["from"], bg["to"], "to bottom right"),
        "decor_color_a":    _rgba(decor_color, 7),    # top-right circle
        "decor_color_b":    _rgba("7FC236",    6),    # bottom-left circle
        # Header
        "heading":          d.get("heading", "Next Steps"),
        "heading_color":    _css(d.get("heading_color", "FFFFFF")),
        "divider_color":    _rgba(d.get("divider_color", "FFFFFF"), 30),
        # Items
        "items": [
            {
                "number":       str(i + 1),
                "badge_color":  _css(item.get("badge_color", "7FC236")),
                "title":        item.get("title", ""),
                "description":  item.get("description", ""),
                "text_color":   _css(item.get("text_color", "FFFFFF")),
            }
            for i, item in enumerate(items)
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# Layout → context builder mapping
# ─────────────────────────────────────────────────────────────────────────────

_LAYOUT_CTX: dict[str, Any] = {
    "I": (_cover_ctx,            "cover.html"),
    "G": (_section_divider_ctx,  "section_divider.html"),
    "H": (_cta_ctx,              "cta.html"),
}


# ─────────────────────────────────────────────────────────────────────────────
# Public renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_to_png(layout_key: str, slide_data: dict) -> bytes:
    """
    Render a visual slide to PNG bytes using Playwright (Chromium headless).

    Parameters
    ----------
    layout_key : str
        One of VISUAL_LAYOUTS ("I", "G", "H").
    slide_data : dict
        Full slide dict from the deck JSON (must include "design" key).

    Returns
    -------
    bytes
        PNG image at 2× retina resolution (2560 × 1440 px).

    Raises
    ------
    RuntimeError
        If Playwright or Chromium is not installed.
    ValueError
        If layout_key is not in VISUAL_LAYOUTS.
    """
    if layout_key not in _LAYOUT_CTX:
        raise ValueError(f"render_to_png: layout {layout_key!r} is not a visual layout")

    ctx_fn, template_name = _LAYOUT_CTX[layout_key]
    ctx = ctx_fn(slide_data)

    template = _jinja_env.get_template(template_name)
    html_content = template.render(**ctx)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Playwright is not installed. Run:\n"
            "  pip install playwright\n"
            "  playwright install chromium"
        ) from exc

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        page = browser.new_page(
            viewport={"width": _VIEWPORT_W, "height": _VIEWPORT_H},
            device_scale_factor=_SCALE,
        )
        page.set_content(html_content, wait_until="networkidle")
        png_bytes = page.screenshot(
            clip={"x": 0, "y": 0, "width": _VIEWPORT_W, "height": _VIEWPORT_H},
            type="png",
        )
        browser.close()

    return png_bytes
