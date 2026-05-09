# vti-slide-renderer

A Python Flask service that accepts a JSON slide deck specification and renders it to a `.pptx` file for download. The renderer is a **faithful typesetter** — it renders exactly what the JSON says, with no design decisions or fallbacks.

---

## Setup

```bash
cd vti-slide-renderer
pip install -r requirements.txt
```

---

## Running the Server

```bash
# Development
python app.py

# Or using Flask CLI
flask run
```

The server starts on `http://localhost:5000`.

---

## API Endpoints

### `POST /render`

Accepts a JSON slide deck, returns a `.pptx` file.

**Request:**
```
Content-Type: application/json
```

**Body:** JSON slide deck (see [JSON Structure](#json-structure))

**Response (success):**
```
Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation
Content-Disposition: attachment; filename="<deck_title>.pptx"
```

**Response (validation error):**
```json
{ "errors": ["error message 1", "error message 2"] }
```
HTTP 400

**Response (render error):**
```json
{ "error": "description" }
```
HTTP 500

---

### `GET /health`

Returns service health status.

```json
{ "status": "ok", "version": "1.0.0" }
```

---

### `GET /schema`

Returns the JSON Schema (Draft-07) for the slide deck input format. Use this to validate your JSON before sending to `/render`.

---

## JSON Structure

```json
{
  "deck_meta": {
    "theme": "VTI",
    "lang": "vi",
    "title": "My Presentation Title"
  },
  "slides": [
    {
      "slide_number": 1,
      "layout": "I",
      "section_idx": 0,
      "design": { ... }
    }
  ]
}
```

See [`schemas/slide_deck.json`](schemas/slide_deck.json) for the full JSON Schema.

### Supported Layouts

| Code | Name              | Notes                          |
|------|-------------------|--------------------------------|
| I    | Cover             | Must be slide_number=1         |
| A    | Card Grid         | n_cols ∈ {2,3,4}; 1 row only  |
| B    | 2-Column List     | Left/right item lists          |
| C    | Flow Steps        | Horizontal or vertical flow    |
| D    | 2-Column Contrast | Left/right card comparison     |
| E    | Data Highlight    | Stats (2–4) + context strip    |
| F    | Narrative         | Long-form body text            |
| G    | Section Divider   | Dark full-bleed chapter marker |
| H    | CTA               | Call-to-action with items      |
| J    | Table of Contents | Auto 1 or 2 columns            |
| K    | Timeline          | Events (3–5) on spine          |
| L    | Icon Grid         | n_cols ∈ {2,3,4} icon cells    |
| M    | Quote             | Large pull-quote format        |

---

## Test with Sample

```bash
curl -X POST http://localhost:5000/render \
  -H "Content-Type: application/json" \
  -d @tests/fixtures/sample_deck.json \
  --output output.pptx
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## How to Add a New Layout

1. **Create layout file** — `renderer/layouts/my_layout.py`
   - Implement `def render(prs, slide_data: dict):`
   - Use only `geometry.py` constants for coordinates
   - Call `inject_footer(slide, slide_data["slide_number"])` as the **last step**

2. **Register in engine.py**
   ```python
   from .layouts import my_layout
   LAYOUT_MAP["X"] = my_layout.render
   ```

3. **Add to JSON Schema** — add `"X"` to the `layout` enum in `schemas/slide_deck.json`

4. **Add semantic validation** (if needed) — update `renderer/validator.py`

5. **Add tests** — create `tests/test_layout_x.py` covering valid render and edge cases

---

## Architecture

```
geometry.py      ← Single source of truth for ALL EMU values
shapes.py        ← Reusable OOXML shape builders (no design decisions)
footer.py        ← Footer injector called last on every slide
validator.py     ← JSON Schema + semantic validation
engine.py        ← Orchestrator: validate → build prs → render slides → return bytes
layouts/         ← One file per layout, calls shapes.py + footer.py
app.py           ← Flask routes: /render, /health, /schema
```

### Key Rules

- **`geometry.py` is the only place with EMU values.** All other modules use `pt()` or named constants.
- **All `bodyPr` must be set explicitly.** `wrap`, `lIns/rIns/tIns/bIns`, `anchor`, `anchorCtr`, and an autofit element are always set.
- **`inject_footer()` is called last in every layout renderer**, unconditionally.
- **No design decisions in renderer.** Render exactly what the JSON says.
- **Semantic icons = OOXML primitives only.** No PIL, no images, no base64.
