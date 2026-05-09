# tests/test_validator.py
import json
from pathlib import Path
import pytest
from renderer.validator import validate

FIXTURES = Path(__file__).parent / "fixtures"


def load_sample():
    with open(FIXTURES / "sample_deck.json", encoding="utf-8") as f:
        return json.load(f)


def test_valid_sample_passes():
    deck = load_sample()
    ok, errors = validate(deck)
    assert ok, f"Expected valid but got errors: {errors}"


def test_missing_deck_meta_fails():
    deck = load_sample()
    del deck["deck_meta"]
    ok, errors = validate(deck)
    assert not ok
    assert any("deck_meta" in e or "required" in e.lower() for e in errors)


def test_missing_slides_fails():
    deck = load_sample()
    del deck["slides"]
    ok, errors = validate(deck)
    assert not ok


def test_non_sequential_slide_numbers_fails():
    deck = load_sample()
    deck["slides"][1]["slide_number"] = 5
    ok, errors = validate(deck)
    assert not ok
    assert any("slide_number" in e for e in errors)


def test_cover_not_slide1_fails():
    deck = load_sample()
    # Add a cover slide at position 2 (slide_number=2)
    import copy
    cover = copy.deepcopy(deck["slides"][0])
    cover["slide_number"] = 2
    deck["slides"].insert(1, cover)
    # Re-number all
    for i, s in enumerate(deck["slides"]):
        s["slide_number"] = i + 1
    # First slide is still cover (slide_number=1) → valid
    # Now make a deck where slide 2 is also layout I (invalid)
    deck2 = load_sample()
    deck2["slides"].append({
        "slide_number": len(deck2["slides"]) + 1,
        "layout": "I",
        "section_idx": 0,
        "design": deck2["slides"][0]["design"]
    })
    ok, errors = validate(deck2)
    assert not ok
    assert any("Cover" in e or "layout" in e.lower() for e in errors)


def test_invalid_n_cols_fails():
    deck = load_sample()
    # Find layout A slide
    for slide in deck["slides"]:
        if slide["layout"] == "A":
            slide["design"]["n_cols"] = 5  # invalid
            break
    ok, errors = validate(deck)
    assert not ok
    assert any("n_cols" in e for e in errors)


def test_stats_count_out_of_range_fails():
    deck = load_sample()
    for slide in deck["slides"]:
        if slide["layout"] == "E":
            slide["design"]["stats"] = [slide["design"]["stats"][0]]  # only 1
            break
    ok, errors = validate(deck)
    assert not ok
    assert any("stats" in e for e in errors)


def test_invalid_hex_in_gradient_fails():
    deck = load_sample()
    deck["slides"][0]["design"]["bg"]["from"] = "ZZZZZZ"
    ok, errors = validate(deck)
    assert not ok
    assert any("hex" in e.lower() for e in errors)
