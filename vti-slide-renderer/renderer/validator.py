# validator.py — JSON schema + semantic validation
from __future__ import annotations

import json
import re
from pathlib import Path

import jsonschema

_SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "slide_deck.json"
_HEX_RE = re.compile(r"^[0-9A-Fa-f]{6}$")


def _load_schema() -> dict:
    with open(_SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _valid_hex(val) -> bool:
    if not isinstance(val, str):
        return False
    return bool(_HEX_RE.match(val))


def _check_gradient(obj: dict, path: str, errors: list):
    if not isinstance(obj, dict):
        return
    for key in ("from", "to"):
        if key in obj and not _valid_hex(obj[key]):
            errors.append(f"{path}.{key} is not a valid 6-char hex: {obj.get(key)!r}")


def validate(deck_json: dict) -> tuple[bool, list[str]]:
    """
    Validate against JSON Schema then run semantic checks.
    Returns (True, []) or (False, ["error message", ...])
    """
    errors: list[str] = []

    # Schema validation
    schema = _load_schema()
    validator = jsonschema.Draft7Validator(schema)
    for err in sorted(validator.iter_errors(deck_json), key=lambda e: e.path):
        errors.append(f"Schema: {err.message} at {list(err.absolute_path)}")

    if errors:
        return False, errors

    slides = deck_json.get("slides", [])

    # Slide numbers sequential starting at 1
    for i, slide in enumerate(slides):
        expected = i + 1
        if slide.get("slide_number") != expected:
            errors.append(
                f"Slide at index {i}: slide_number must be {expected}, "
                f"got {slide.get('slide_number')}"
            )

    # Layout I must be slide_number=1
    for slide in slides:
        if slide.get("layout") == "I" and slide.get("slide_number") != 1:
            errors.append("Layout 'I' (Cover) must have slide_number=1")

    for slide in slides:
        layout = slide.get("layout", "")
        design = slide.get("design", {})
        sn = slide.get("slide_number")

        if layout in ("A", "L"):
            n_cols = design.get("n_cols")
            if n_cols not in (2, 3, 4):
                errors.append(
                    f"Slide {sn} layout {layout}: n_cols must be 2, 3, or 4, got {n_cols!r}"
                )

        if layout == "A":
            n_cols = design.get("n_cols", 0)
            cards = design.get("cards", [])
            if len(cards) != n_cols:
                errors.append(
                    f"Slide {sn} layout A: cards length ({len(cards)}) "
                    f"must equal n_cols ({n_cols})"
                )

        if layout == "E":
            stats = design.get("stats", [])
            if not (2 <= len(stats) <= 4):
                errors.append(
                    f"Slide {sn} layout E: stats length must be 2-4, got {len(stats)}"
                )

        if layout == "K":
            events = design.get("events", [])
            if not (3 <= len(events) <= 5):
                errors.append(
                    f"Slide {sn} layout K: events length must be 3-5, got {len(events)}"
                )

        # Validate gradient hex colors in design
        for field_name, field_val in design.items():
            if isinstance(field_val, dict) and "from" in field_val:
                _check_gradient(field_val, f"slide {sn}.design.{field_name}", errors)
            elif isinstance(field_val, list):
                for j, item in enumerate(field_val):
                    if isinstance(item, dict):
                        for sub_key, sub_val in item.items():
                            if isinstance(sub_val, dict) and "from" in sub_val:
                                _check_gradient(
                                    sub_val,
                                    f"slide {sn}.design.{field_name}[{j}].{sub_key}",
                                    errors
                                )

    return (len(errors) == 0), errors
