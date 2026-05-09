# GitHub Copilot Prompt — Flask PPTX Renderer
> Paste prompt này vào GitHub Copilot Chat (Agent mode) để build project.

---

## PROMPT

Build a Python Flask project called **`vti-slide-renderer`** that receives a JSON slide deck specification from an HTTP POST request and renders it into a `.pptx` file for download. The JSON is produced by an AI (Gemini) acting as designer — the renderer must be a **faithful typesetter**: no design decisions, no fallbacks to defaults, render exactly what the JSON says.

---

### Project structure

```
vti-slide-renderer/
├── app.py                  # Flask entry point
├── renderer/
│   ├── __init__.py
│   ├── engine.py           # Main render orchestrator
│   ├── geometry.py         # EMU math — ALL coordinate calculations live here
│   ├── shapes.py           # Shape builders (gradient, roundRect, textbox, badge, icon)
│   ├── layouts/
│   │   ├── __init__.py
│   │   ├── cover.py        # Layout I
│   │   ├── card_grid.py    # Layout A
│   │   ├── two_col_list.py # Layout B
│   │   ├── flow_steps.py   # Layout C
│   │   ├── two_col_contrast.py  # Layout D
│   │   ├── data_highlight.py    # Layout E
│   │   ├── narrative.py    # Layout F
│   │   ├── section_divider.py   # Layout G
│   │   ├── cta.py          # Layout H
│   │   ├── toc.py          # Layout J
│   │   ├── timeline.py     # Layout K
│   │   ├── icon_grid.py    # Layout L
│   │   └── quote.py        # Layout M
│   ├── footer.py           # Footer injector (mandatory every slide)
│   └── validator.py        # JSON schema validation before render
├── schemas/
│   └── slide_deck.json     # JSON Schema (Draft-07) for input validation
├── tests/
│   ├── test_geometry.py
│   ├── test_shapes.py
│   └── fixtures/
│       └── sample_deck.json
├── requirements.txt
└── README.md
```

---

### Tech stack

```
Flask>=3.0
python-pptx>=0.6.23
jsonschema>=4.21
lxml>=5.0
pytest
```

---

### geometry.py — The single source of truth for all coordinates

This module must define ALL constants and ALL coordinate math. No other module may hardcode EMU values.

```python
# ── Slide dimensions ──────────────────────────────────────────────────
SLIDE_W = 12192000   # 960pt × 12700
SLIDE_H = 6858000    # 540pt × 12700
PT      = 12700      # 1pt in EMU

def pt(n: float) -> int:
    """Convert points to EMU. Use everywhere instead of raw numbers."""
    return int(n * PT)

# ── Content Zone Budget ───────────────────────────────────────────────
MARGIN_X        = pt(20)
CONTENT_X       = pt(20)
CONTENT_W       = pt(920)   # SLIDE_W - 2 × MARGIN_X
ACCENT_BAR_Y    = pt(85)
ACCENT_BAR_H    = pt(4)
CONTENT_TOP     = pt(105)
CONTENT_BOTTOM  = pt(480)
CONTENT_H       = pt(375)   # CONTENT_BOTTOM - CONTENT_TOP
FOOTER_Y        = pt(502)
CARD_GAP        = pt(10)
COL_GAP         = pt(10)

# ── Stretch-to-fill formulas ──────────────────────────────────────────
def card_h(n_rows: int) -> int:
    """Dynamic card height that always fills CONTENT_H."""
    return (CONTENT_H - CARD_GAP * (n_rows - 1)) // n_rows

def card_y(row_idx: int, n_rows: int) -> int:
    return CONTENT_TOP + row_idx * (card_h(n_rows) + CARD_GAP)

def card_w(n_cols: int) -> int:
    return (CONTENT_W - COL_GAP * (n_cols - 1)) // n_cols

def card_x(col_idx: int, n_cols: int) -> int:
    return CONTENT_X + col_idx * (card_w(n_cols) + COL_GAP)

# ── Footer fixed positions ────────────────────────────────────────────
FOOTER_NUM_X    = 453839
FOOTER_NUM_Y    = 6375400
FOOTER_NUM_W    = 533400
FOOTER_NUM_H    = 438551
FOOTER_COPY_X   = 1066800
FOOTER_COPY_Y   = 6413000
FOOTER_COPY_W   = 3175000
FOOTER_COPY_H   = 342900

# ── bodyPr inset constants ────────────────────────────────────────────
INS_CARD   = dict(lIns=pt(12), rIns=pt(12), tIns=pt(9),  bIns=pt(9))
INS_HEADER = dict(lIns=pt(12), rIns=pt(12), tIns=pt(6),  bIns=pt(6))
INS_FOOTER = dict(lIns=pt(6),  rIns=pt(6),  tIns=0,       bIns=0)
INS_NONE   = dict(lIns=0,      rIns=0,       tIns=0,       bIns=0)
```

---

### JSON input contract

The renderer accepts a POST to `/render` with `Content-Type: application/json`.

**Top-level structure:**
```json
{
  "deck_meta": {
    "theme": "VTI",
    "lang": "vi",
    "title": "Deck title for filename"
  },
  "slides": [ ...slide objects... ]
}
```

**Every slide object has:**
```json
{
  "slide_number": 1,
  "layout": "I",
  "section_idx": 0,
  "design": { ...layout-specific design fields... }
}
```

**The `design` object structure is polymorphic by `layout`.**

Implement the following `design` schemas:

#### Layout I — Cover
```json
{
  "tag": "VTI JAPAN 2026",
  "title": "Main Title Text",
  "subtitle": "Subtitle text here",
  "caption": "Date or context",
  "bg": { "from": "FFFFFF", "to": "EEF4FB", "angle": 9000000 },
  "left_bar": { "from": "172759", "to": "2362B0" },
  "right_strip": { "from": "2362B0", "to": "4A9EE0", "opacity": 30 },
  "title_color": "172759",
  "tag_color": "2362B0",
  "subtitle_color": "172759",
  "caption_color": "6A7FA0",
  "divider_bar": { "from": "2362B0", "to": "7FC236" },
  "right_card": {
    "tint": "A",
    "icon": { "type": "ai", "stroke": "4A9EE0", "size_pt": 80 }
  }
}
```

#### Layout A — Card Grid
```json
{
  "title": "Slide title",
  "breadcrumb": "Section name",
  "accent_bar": { "from": "2362B0", "to": "7FC236", "angle": 5400000 },
  "bg": { "from": "FFFFFF", "to": "EEF4FB", "angle": 9000000 },
  "n_cols": 3,
  "cards": [
    {
      "tint": "A",
      "header": "Card title",
      "header_color": "172759",
      "bg": { "from": "EBF4FC", "to": "D6EAF8" },
      "border_top": "4A9EE0",
      "icon": { "type": "ai", "stroke": "4A9EE0", "size_pt": 36 },
      "bullets": [
        { "text": "Bullet text", "dot_color": "4A9EE0" }
      ],
      "text_color": "1C2D4F"
    }
  ]
}
```

#### Layout B — 2-Column List
```json
{
  "title": "Slide title",
  "breadcrumb": "Section",
  "accent_bar": { "from": "2362B0", "to": "7FC236", "angle": 5400000 },
  "bg": { "from": "FFFFFF", "to": "EEF4FB", "angle": 9000000 },
  "separator_color": "B8D0EE",
  "left_items": [
    { "text": "Item text", "badge_color": "2362B0", "text_color": "1C2D4F" }
  ],
  "right_items": [
    { "text": "Item text", "badge_color": "1E9E8A", "text_color": "1C2D4F" }
  ]
}
```

#### Layout C — Flow Steps
```json
{
  "title": "Slide title",
  "breadcrumb": "Section",
  "accent_bar": { "from": "2362B0", "to": "7FC236", "angle": 5400000 },
  "bg": { "from": "FFFFFF", "to": "EEF4FB", "angle": 9000000 },
  "flow_direction": "horizontal",
  "arrow_color": "B8D0EE",
  "steps": [
    {
      "tint": "A",
      "bg": { "from": "EBF4FC", "to": "D6EAF8" },
      "border_top": "4A9EE0",
      "badge_color": "2362B0",
      "header": "Step title",
      "header_color": "172759",
      "description": "Short description",
      "text_color": "1C2D4F"
    }
  ]
}
```

#### Layout E — Data Highlight
```json
{
  "title": "Slide title",
  "breadcrumb": "Section",
  "accent_bar": { "from": "2362B0", "to": "7FC236", "angle": 5400000 },
  "bg": { "from": "FFFFFF", "to": "EEF4FB", "angle": 9000000 },
  "stats": [
    {
      "tint": "A",
      "bg": { "from": "EBF4FC", "to": "D6EAF8" },
      "number": "98%",
      "number_color": "2362B0",
      "unit": "",
      "label": "Completion rate",
      "label_color": "6A7FA0"
    }
  ],
  "context_text": "Supporting context sentence.",
  "context_bg": { "from": "EEF4FB", "to": "FFFFFF" },
  "context_text_color": "1C2D4F"
}
```

#### Layout G — Section Divider
```json
{
  "bg": { "from": "172759", "to": "1A3070", "angle": 9000000 },
  "left_bar": { "from": "2362B0", "to": "7FC236" },
  "section_number": "01",
  "section_number_color": "6A7FA0",
  "section_title": "Chapter title",
  "section_title_color": "FFFFFF",
  "subtitle": "Chapter subtitle",
  "subtitle_color": "B8D0EE",
  "right_card": {
    "tint": "A",
    "bg": { "from": "EBF4FC", "to": "D6EAF8" },
    "icon": { "type": "settings", "stroke": "4A9EE0", "size_pt": 64 }
  },
  "decor": { "color": "1A3070", "opacity": 20 }
}
```

#### Layout H — CTA
```json
{
  "bg": { "from": "2362B0", "to": "172759", "angle": 16200000 },
  "heading": "Next Steps",
  "heading_color": "FFFFFF",
  "items": [
    { "badge_color": "7FC236", "title": "Action 1", "description": "Details", "text_color": "FFFFFF" }
  ],
  "divider_color": "FFFFFF",
  "decor_color": "2362B0"
}
```

#### Layout K — Timeline
```json
{
  "title": "Slide title",
  "breadcrumb": "Section",
  "accent_bar": { "from": "2362B0", "to": "7FC236", "angle": 5400000 },
  "bg": { "from": "FFFFFF", "to": "EEF4FB", "angle": 9000000 },
  "spine": { "from": "2362B0", "to": "7FC236" },
  "events": [
    {
      "date": "Q1 2026",
      "label": "Milestone name",
      "description": "Short detail",
      "tint": "A",
      "bg": { "from": "EBF4FC", "to": "D6EAF8" },
      "dot_color": "2362B0",
      "text_color": "1C2D4F",
      "date_color": "6A7FA0"
    }
  ]
}
```

#### Layout L — Icon Grid
```json
{
  "title": "Slide title",
  "breadcrumb": "Section",
  "accent_bar": { "from": "2362B0", "to": "7FC236", "angle": 5400000 },
  "bg": { "from": "FFFFFF", "to": "EEF4FB", "angle": 9000000 },
  "n_cols": 3,
  "cells": [
    {
      "tint": "A",
      "bg": { "from": "EBF4FC", "to": "D6EAF8" },
      "border_top": "4A9EE0",
      "icon": { "type": "ai", "stroke": "4A9EE0", "size_pt": 36 },
      "label": "Feature name",
      "label_color": "172759",
      "sub_label": "Short description",
      "sub_label_color": "6A7FA0"
    }
  ]
}
```

---

### shapes.py — Core shape builders

Implement these functions. All use `lxml` to build OOXML directly where python-pptx is insufficient.

```python
def add_gradient_fill(shape, from_hex, to_hex, angle_emu, stops=None):
    """
    Apply gradient fill to any shape via OOXML injection.
    stops: optional list of (position_0_to_100000, hex) for multi-stop gradients.
    If stops is None, build 2-stop gradient from from_hex to to_hex.
    """

def add_rounded_rect(slide, x, y, w, h, from_hex, to_hex,
                     angle_emu=16200000, border_hex=None, border_w_pt=0):
    """
    Add roundRect shape (adj=16667 = ~corner radius 13%).
    Optional top border as separate thin rect if border_hex provided.
    Returns the shape object.
    """

def add_textbox_styled(slide, x, y, w, h, text,
                       font_name, size_pt, color_hex,
                       bold=False, italic=False,
                       align="left", v_anchor="t",
                       wrap=True, inset=None, autofit="norm",
                       line_spacing=None, lang="vi-VN"):
    """
    Add textbox with full bodyPr:
      wrap: True → wrap="square", False → wrap="none"
      inset: one of INS_CARD | INS_HEADER | INS_FOOTER | INS_NONE | custom dict
      autofit: "norm" → normAutofit, "none" → noAutofit, "sp" → spAutoFit
      lang: "vi-VN" | "ja-JP"
    NEVER allow text to overflow shape boundary.
    """

def add_badge(slide, x, y, number_or_text, bg_hex, text_hex="FFFFFF", size_pt=40):
    """
    Circular badge (ellipse) with centered number/text.
    size_pt applies to both width and height of the circle.
    """

def add_dot_bullet(slide, x, y, dot_hex, size_pt=6):
    """Small filled circle for bullet points."""

def add_separator_line(slide, x, y, w, h, color_hex):
    """Thin rect used as horizontal or vertical separator."""

def add_semantic_icon(slide, x, y, size_pt, stroke_hex, icon_type):
    """
    OOXML geometric icon — stroke-only, no bitmap.
    icon_type: "ai" | "settings" | "data" | "flow" | "doc" |
               "team" | "check" | "chart" | "lock" | "star" | "default"
    stroke_width_pt: 2.0 for hero (≥80pt), 1.5 for others
    Each icon_type renders as 2-3 stacked OOXML primitive shapes
    (ellipse, roundRect, line combinations) that suggest the semantic.
    "default" → single ellipse (always safe fallback).
    Returns list of shapes added.
    """
```

---

### footer.py — Injected on every slide, no exceptions

```python
def inject_footer(slide, slide_number: int):
    """
    Insert footer into slide. Called LAST after all content shapes.
    Fixed positions from geometry.py constants — NEVER modify coordinates.

    Shape 1: Filled rect at (FOOTER_NUM_X, FOOTER_NUM_Y, FOOTER_NUM_W, FOOTER_NUM_H)
             fill = #408DD6 (constant, never changes with theme)
             text = slide_number, Arial 18pt bold white, centered

    Shape 2: Transparent textbox at (FOOTER_COPY_X, FOOTER_COPY_Y, FOOTER_COPY_W, FOOTER_COPY_H)
             text = "Copyright © 2026 VTI All rights reserved"
             Arial 10pt, color #808080, wrap=none (single line guaranteed by cx=3175000)
    """
```

---

### engine.py — Orchestrator

```python
LAYOUT_MAP = {
    "I": cover.render,
    "A": card_grid.render,
    "B": two_col_list.render,
    "C": flow_steps.render,
    "D": two_col_contrast.render,
    "E": data_highlight.render,
    "F": narrative.render,
    "G": section_divider.render,
    "H": cta.render,
    "J": toc.render,
    "K": timeline.render,
    "L": icon_grid.render,
    "M": quote.render,
}

def render_deck(deck_json: dict) -> bytes:
    """
    1. Validate JSON against schema (validator.py) — raise 400 if invalid
    2. Create Presentation with SLIDE_W × SLIDE_H
    3. For each slide: call LAYOUT_MAP[slide["layout"]](prs, slide)
    4. Each layout renderer calls inject_footer(slide, slide_number) as final step
    5. Save to BytesIO, return bytes
    """
```

---

### validator.py

```python
def validate(deck_json: dict) -> tuple[bool, list[str]]:
    """
    Validate against JSON Schema in schemas/slide_deck.json.
    Also run semantic checks that schema can't catch:
    - slide_number must be sequential starting at 1
    - layout "I" must be slide_number=1
    - n_cols in [2,3,4] for layouts A and L
    - cards length must equal n_cols for layout A (1 row)
    - stats length in [2,3,4] for layout E
    - events length in [3,4,5] for layout K
    - gradient hex values: must be valid 6-char hex, no # prefix
    Returns (True, []) or (False, ["error message 1", ...])
    """
```

---

### app.py — Flask routes

```python
@app.route("/render", methods=["POST"])
def render():
    """
    Accept JSON body. Return .pptx file download.
    Response headers:
      Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation
      Content-Disposition: attachment; filename="{deck_title}.pptx"
    On validation error → 400 JSON with {"errors": [...]}
    On render error → 500 JSON with {"error": "..."}
    """

@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "version": "1.0.0"}

@app.route("/schema", methods=["GET"])
def schema():
    """Return the JSON schema so Gemini can reference it."""
    return jsonify(load_schema())
```

---

### Implementation rules — enforce these without exception

1. **geometry.py is the only place with EMU values.** If any other file needs a coordinate, it calls `pt()` or references a constant from geometry.py.

2. **All bodyPr must be set explicitly.** Never leave `<a:bodyPr/>` empty. Every textbox gets `wrap`, `lIns/rIns/tIns/bIns`, `anchor`, `anchorCtr`, and either `normAutofit` or `noAutofit`.

3. **inject_footer() is called last in every layout renderer.** Not optional, not conditional.

4. **No design decisions in renderer.** If a JSON field says `"color": "E05060"`, render `E05060`. Do not substitute, validate against theme, or default to a "better" color.

5. **Gradient angles from JSON.** The JSON provides `angle` in EMU units (e.g. 9000000 = 270°). Pass directly to OOXML `<a:lin ang="{angle}"/>`.

6. **Semantic icons = OOXML shapes only.** No PIL, no image files, no base64 PNG. Build from ellipse/roundRect/line primitives.

7. **card_h() and card_w() from geometry.py only.** Never hardcode card dimensions in layout files.

8. **Tests.** Write pytest tests in `tests/` for: geometry math, footer positions, gradient OOXML output, validator accepting valid JSON, validator rejecting missing fields.

---

### Sample request for testing

```bash
curl -X POST http://localhost:5000/render \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sample_deck.json \
  --output output.pptx
```

Write `tests/fixtures/sample_deck.json` with 4 slides: Cover (I), Section Divider (G), Card Grid A with 3 cards, Data Highlight E with 3 stats. Use VTI theme, Vietnamese language.

---

### README.md must include

- Setup instructions (`pip install -r requirements.txt`)
- How to run (`flask run` or `python app.py`)
- API endpoint docs (POST /render, GET /health, GET /schema)
- JSON structure overview with link to schema
- How to add a new layout (checklist: create layout file, register in LAYOUT_MAP, add schema, add test)
