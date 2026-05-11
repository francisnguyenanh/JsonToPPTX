"""
Design System Engine.

Resolves semantic intent JSON (what Gemini generates) into full design JSON
(what the existing renderers consume via slide_data["design"]).

Intent JSON has ONLY content + layout decisions — no hex colors, no gradients,
no tint values.  All visual parameters are derived here from the chosen theme.

Public API:
    resolve_deck(deck: dict) -> dict   # adds "design" key to each slide
    resolve_slide(slide: dict, th: dict) -> dict
"""
from __future__ import annotations

# ── Gradient angle constants (EMU units) ─────────────────────────────────────
ANG_TOP_BOTTOM = 9000000    # slide backgrounds (top → bottom)
ANG_LEFT_RIGHT = 5400000    # accent bars (left → right)
ANG_BTM_TOP    = 16200000   # card fills (bottom → top)
ANG_VERTICAL   = 0          # cover / section left bar

_TINT_KEYS = ["A", "B", "C", "D", "E", "F"]

# ── Theme tables ──────────────────────────────────────────────────────────────
_THEMES: dict[str, dict] = {
    "VTI": {
        "slide_bg":       {"from": "FFFFFF", "to": "EEF4FB"},
        "accent_bar":     {"from": "2362B0", "to": "7FC236"},
        "title_color":    "172759",
        "body_color":     "1C2D4F",
        "muted_color":    "6A7FA0",
        "separator_color":"B8D0EE",
        "card_body":      "FCFDFD",
        "tints": {
            "A": {"bg_from": "F4F9FE", "bg_to": "EAF3FB", "border": "4A9EE0"},
            "B": {"bg_from": "F0FAF7", "bg_to": "E3F6F0", "border": "1E9E8A"},
            "C": {"bg_from": "FFFCF3", "bg_to": "FEF5E0", "border": "E8A020"},
            "D": {"bg_from": "FFF4F5", "bg_to": "FDEAEC", "border": "E05060"},
            "E": {"bg_from": "EFF5FD", "bg_to": "E4EEF9", "border": "2362B0"},
            "F": {"bg_from": "F3FBF0", "bg_to": "E8F7E1", "border": "7FC236"},
        },
        "section_rotation": [
            {"badge": "2362B0", "alt": "7FC236", "stat": "1E9E8A"},
            {"badge": "1E9E8A", "alt": "4A9EE0", "stat": "E8A020"},
            {"badge": "7FC236", "alt": "E8A020", "stat": "2362B0"},
        ],
        "cover_left_bar":    {"from": "172759", "to": "2362B0"},
        "cover_right_strip": {"from": "2362B0", "to": "4A9EE0", "opacity": 30},
        "cover_divider_bar": {"from": "2362B0", "to": "7FC236"},
        "section_divider_bg":       {"from": "172759", "to": "1A3070"},
        "section_divider_decor":    "1A3070",
        "section_divider_title":    "FFFFFF",
        "section_divider_subtitle": "B8D0EE",
        "cta_bg":           {"from": "2362B0", "to": "172759"},
        "cta_badge_colors": ["7FC236", "4A9EE0", "1E9E8A"],
        "cta_decor_color":  "2362B0",
    },
    "Dark": {
        "slide_bg":       {"from": "1C1C2E", "to": "12121F"},
        "accent_bar":     {"from": "D4A26A", "to": "8DAAC2"},
        "title_color":    "E0E2E5",
        "body_color":     "D8DAE0",
        "muted_color":    "8A8CA0",
        "separator_color":"3A3A5A",
        "card_body":      "252538",
        "tints": {
            "A": {"bg_from": "2A2840", "bg_to": "222038", "border": "D4A26A"},
            "B": {"bg_from": "223040", "bg_to": "1A2836", "border": "8DAAC2"},
            "C": {"bg_from": "2A2838", "bg_to": "202030", "border": "5EC4B0"},
            "D": {"bg_from": "2E2438", "bg_to": "261C30", "border": "D4A26A"},
            "E": {"bg_from": "22284A", "bg_to": "1A203E", "border": "8DAAC2"},
            "F": {"bg_from": "20302E", "bg_to": "182824", "border": "5EC4B0"},
        },
        "section_rotation": [
            {"badge": "D4A26A", "alt": "8DAAC2", "stat": "D4A26A"},
            {"badge": "8DAAC2", "alt": "5EC4B0", "stat": "8DAAC2"},
            {"badge": "5EC4B0", "alt": "D4A26A", "stat": "5EC4B0"},
        ],
        "cover_left_bar":    {"from": "D4A26A", "to": "8DAAC2"},
        "cover_right_strip": {"from": "8DAAC2", "to": "5EC4B0", "opacity": 30},
        "cover_divider_bar": {"from": "D4A26A", "to": "8DAAC2"},
        "section_divider_bg":       {"from": "1C1C2E", "to": "12121F"},
        "section_divider_decor":    "2E2E4A",
        "section_divider_title":    "E0E2E5",
        "section_divider_subtitle": "8A8CA0",
        "cta_bg":           {"from": "12121F", "to": "1C1C2E"},
        "cta_badge_colors": ["D4A26A", "8DAAC2", "5EC4B0"],
        "cta_decor_color":  "252538",
    },
    "Light": {
        "slide_bg":       {"from": "F5F4F0", "to": "ECEAE4"},
        "accent_bar":     {"from": "3B6FA0", "to": "C06030"},
        "title_color":    "1A1A2E",
        "body_color":     "2E2E3A",
        "muted_color":    "8A9BAD",
        "separator_color":"A3B5B8",
        "card_body":      "FAFBFF",
        "tints": {
            "A": {"bg_from": "FAFBFF", "bg_to": "F0F3FA", "border": "3B6FA0"},
            "B": {"bg_from": "FFF9F5", "bg_to": "F8EDE4", "border": "C06030"},
            "C": {"bg_from": "F5FDFB", "bg_to": "E8F8F4", "border": "2A9080"},
            "D": {"bg_from": "FAFBFF", "bg_to": "EFF3FA", "border": "3B6FA0"},
            "E": {"bg_from": "FFF9F5", "bg_to": "F8EDE4", "border": "C06030"},
            "F": {"bg_from": "F5FDFB", "bg_to": "E8F8F4", "border": "2A9080"},
        },
        "section_rotation": [
            {"badge": "3B6FA0", "alt": "C06030", "stat": "3B6FA0"},
            {"badge": "C06030", "alt": "2A9080", "stat": "C06030"},
            {"badge": "2A9080", "alt": "3B6FA0", "stat": "2A9080"},
        ],
        "cover_left_bar":    {"from": "3B6FA0", "to": "C06030"},
        "cover_right_strip": {"from": "C06030", "to": "2A9080", "opacity": 30},
        "cover_divider_bar": {"from": "3B6FA0", "to": "C06030"},
        "section_divider_bg":       {"from": "F5F4F0", "to": "ECEAE4"},
        "section_divider_decor":    "A3B5B8",
        "section_divider_title":    "1A1A2E",
        "section_divider_subtitle": "8A9BAD",
        "cta_bg":           {"from": "ECEAE4", "to": "F5F4F0"},
        "cta_badge_colors": ["3B6FA0", "C06030", "2A9080"],
        "cta_decor_color":  "A3B5B8",
    },
    "Kimi": {
        "slide_bg":       {"from": "F5F6F8", "to": "EBEDF2"},
        "accent_bar":     {"from": "2E5E8A", "to": "FF7F50"},
        "title_color":    "3C4A5A",
        "body_color":     "3C4A5A",
        "muted_color":    "6B9CBF",
        "separator_color":"C5D5E4",
        "card_body":      "FCFDFD",
        "tints": {
            "A": {"bg_from": "FCFDFD", "bg_to": "F4F8FC", "border": "2E5E8A"},
            "B": {"bg_from": "FCFDFD", "bg_to": "FFF5F2", "border": "FF7F50"},
            "C": {"bg_from": "FCFDFD", "bg_to": "F0F6FB", "border": "6B9CBF"},
            "D": {"bg_from": "FCFDFD", "bg_to": "F4F8FC", "border": "2E5E8A"},
            "E": {"bg_from": "FCFDFD", "bg_to": "FFF5F2", "border": "FF7F50"},
            "F": {"bg_from": "FCFDFD", "bg_to": "F0F6FB", "border": "6B9CBF"},
        },
        "section_rotation": [
            {"badge": "2E5E8A", "alt": "FF7F50", "stat": "6B9CBF"},
            {"badge": "FF7F50", "alt": "6B9CBF", "stat": "2E5E8A"},
            {"badge": "6B9CBF", "alt": "2E5E8A", "stat": "FF7F50"},
        ],
        "cover_left_bar":    {"from": "2E5E8A", "to": "3C4A5A"},
        "cover_right_strip": {"from": "2E5E8A", "to": "6B9CBF", "opacity": 25},
        "cover_divider_bar": {"from": "2E5E8A", "to": "FF7F50"},
        "section_divider_bg":       {"from": "2E3A4A", "to": "1C2A3A"},
        "section_divider_decor":    "3C4A5A",
        "section_divider_title":    "FCFDFD",
        "section_divider_subtitle": "6B9CBF",
        "cta_bg":           {"from": "2E5E8A", "to": "1C2A3A"},
        "cta_badge_colors": ["FF7F50", "6B9CBF", "2E5E8A"],
        "cta_decor_color":  "2E5E8A",
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _grad(from_hex: str, to_hex: str, angle: int = ANG_BTM_TOP) -> dict:
    return {"from": from_hex, "to": to_hex, "angle": angle}


def _tint(th: dict, idx: int) -> dict:
    return th["tints"][_TINT_KEYS[idx % 6]]


def _tint_key(idx: int) -> str:
    return _TINT_KEYS[idx % 6]


def _sec(th: dict, section_idx: int) -> dict:
    return th["section_rotation"][section_idx % 3]


def _bullets(raw: list, dot_color: str) -> list[dict]:
    result = []
    for b in raw:
        text = b if isinstance(b, str) else b.get("text", "")
        if text:
            result.append({"text": text, "dot_color": dot_color})
    return result


def _card(intent: dict, idx: int, th: dict, icon_size: int = 36) -> dict:
    t = _tint(th, idx)
    border = t["border"]
    card = {
        "tint": _tint_key(idx),
        "bg": _grad(t["bg_from"], t["bg_to"]),
        "border_top": border,
        "card_body": th.get("card_body", "FCFDFD"),
        "header": intent.get("header", ""),
        "header_color": th["title_color"],
        "bullets": _bullets(intent.get("bullets", []), border),
        "text_color": th["body_color"],
    }
    icon_type = intent.get("icon_type")
    if icon_type:
        card["icon"] = {"type": icon_type, "stroke": border, "size_pt": icon_size}
    return card


def _common(slide: dict, th: dict) -> dict:
    return {
        "title": slide.get("title", ""),
        "title_color": th["title_color"],
        "breadcrumb": slide.get("breadcrumb", ""),
        "breadcrumb_color": th["muted_color"],
        "bg": _grad(th["slide_bg"]["from"], th["slide_bg"]["to"], ANG_TOP_BOTTOM),
        "accent_bar": _grad(th["accent_bar"]["from"], th["accent_bar"]["to"], ANG_LEFT_RIGHT),
    }


# ── Layout resolvers ──────────────────────────────────────────────────────────

def _cover(s: dict, th: dict) -> dict:
    t = _tint(th, 0)
    border = t["border"]
    lb = th["cover_left_bar"]
    rs = th["cover_right_strip"]
    db = th["cover_divider_bar"]
    return {
        "tag": s.get("tag", ""),
        "tag_color": th["accent_bar"]["from"],
        "title": s.get("title", ""),
        "title_color": th["title_color"],
        "subtitle": s.get("subtitle", ""),
        "subtitle_color": th["title_color"],
        "caption": s.get("caption", ""),
        "caption_color": th["muted_color"],
        "bg": _grad(th["slide_bg"]["from"], th["slide_bg"]["to"], ANG_TOP_BOTTOM),
        "left_bar": _grad(lb["from"], lb["to"], ANG_VERTICAL),
        "right_strip": {**rs, "angle": 0},
        "divider_bar": _grad(db["from"], db["to"], ANG_LEFT_RIGHT),
        "right_card": {
            "tint": _tint_key(0),
            "bg": _grad(t["bg_from"], t["bg_to"]),
            "border_top": border,
            "icon": {"type": s.get("right_icon_type", "ai"), "stroke": border, "size_pt": 80},
        },
    }


def _card_grid(s: dict, th: dict) -> dict:
    d = _common(s, th)
    cards = s.get("cards", [])
    d["n_cols"] = len(cards)
    d["cards"] = [_card(c, i, th, 36) for i, c in enumerate(cards)]
    return d


def _two_col_list(s: dict, th: dict) -> dict:
    d = _common(s, th)
    d["separator_color"] = th["separator_color"]
    sec = th["section_rotation"]
    cycle = [sec[0]["badge"], sec[1]["badge"], sec[0]["alt"], sec[1]["alt"]]

    def _items(raw: list, offset: int) -> list[dict]:
        result = []
        for i, item in enumerate(raw):
            text = item if isinstance(item, str) else item.get("text", "")
            result.append({
                "text": text,
                "badge_color": cycle[(offset + i) % len(cycle)],
                "text_color": th["body_color"],
            })
        return result

    left = s.get("left_items", [])
    d["left_items"] = _items(left, 0)
    d["right_items"] = _items(s.get("right_items", []), len(left))
    return d


def _flow_steps(s: dict, th: dict) -> dict:
    d = _common(s, th)
    d["flow_direction"] = s.get("flow_direction", "horizontal")
    d["arrow_color"] = th["separator_color"]
    badge_color = _sec(th, s.get("section_idx", 0))["badge"]
    steps = []
    for i, step in enumerate(s.get("steps", [])):
        t = _tint(th, i)
        border = t["border"]
        steps.append({
            "tint": _tint_key(i),
            "bg": _grad(t["bg_from"], t["bg_to"]),
            "border_top": border,
            "badge_color": badge_color,
            "header": step.get("header", ""),
            "header_color": th["title_color"],
            "description": step.get("description", ""),
            "text_color": th["body_color"],
        })
    d["steps"] = steps
    return d


def _two_col_contrast(s: dict, th: dict) -> dict:
    d = _common(s, th)
    d["vs_label_color"] = th["muted_color"]

    def _side(header: str, raw_bullets: list, tint_idx: int) -> dict:
        t = _tint(th, tint_idx)
        border = t["border"]
        return {
            "tint": _tint_key(tint_idx),
            "bg": _grad(t["bg_from"], t["bg_to"]),
            "border_top": border,
            "card_body": th.get("card_body", "FCFDFD"),
            "header": header,
            "header_color": th["title_color"],
            "bullets": _bullets(raw_bullets, border),
            "text_color": th["body_color"],
        }

    d["left_card"]  = _side(s.get("left_header", ""),  s.get("left_bullets", []),  4)  # Tint E
    d["right_card"] = _side(s.get("right_header", ""), s.get("right_bullets", []), 5)  # Tint F
    return d


def _data_highlight(s: dict, th: dict) -> dict:
    d = _common(s, th)
    stat_color = _sec(th, s.get("section_idx", 0))["stat"]
    stats = []
    for i, stat in enumerate(s.get("stats", [])):
        t = _tint(th, i)
        stats.append({
            "tint": _tint_key(i),
            "bg": _grad(t["bg_from"], t["bg_to"]),
            "number": stat.get("number", ""),
            "number_color": stat_color,
            "unit": stat.get("unit", ""),
            "label": stat.get("label", ""),
            "label_color": th["muted_color"],
        })
    d["stats"] = stats
    d["context_text"] = s.get("context_text", "")
    d["context_bg"] = _grad(th["slide_bg"]["to"], th["slide_bg"]["from"])
    d["context_text_color"] = th["body_color"]
    return d


def _narrative(s: dict, th: dict) -> dict:
    d = _common(s, th)
    t = _tint(th, 0)
    border = t["border"]
    d["left_panel"] = {
        "body_text": s.get("body_text", ""),
        "text_color": th["body_color"],
        "bullets": _bullets(s.get("bullets", []), border),
    }
    d["right_panel"] = {
        "tint": _tint_key(0),
        "bg": _grad(t["bg_from"], t["bg_to"]),
        "border_top": border,
        "icon": {"type": s.get("right_icon_type", "default"), "stroke": border, "size_pt": 56},
        "callout_number": s.get("callout_number", ""),
        "callout_label":  s.get("callout_label", ""),
    }
    return d


def _section_divider(s: dict, th: dict) -> dict:
    sec_idx = s.get("section_idx", 0)
    t = _tint(th, sec_idx)
    border = t["border"]
    bg = th["section_divider_bg"]
    return {
        "bg": _grad(bg["from"], bg["to"], ANG_TOP_BOTTOM),
        "left_bar": _grad(th["accent_bar"]["from"], th["accent_bar"]["to"], ANG_VERTICAL),
        "section_number": s.get("section_number", ""),
        "section_number_color": th["muted_color"],
        "section_title": s.get("section_title", ""),
        "section_title_color": th["section_divider_title"],
        "subtitle": s.get("subtitle", ""),
        "subtitle_color": th["section_divider_subtitle"],
        "right_card": {
            "tint": _tint_key(sec_idx),
            "bg": _grad(t["bg_from"], t["bg_to"]),
            "border_top": border,
            "icon": {"type": s.get("icon_type", "settings"), "stroke": border, "size_pt": 64},
        },
        "decor": {"color": th["section_divider_decor"], "opacity": 20},
    }


def _cta(s: dict, th: dict) -> dict:
    bg = th["cta_bg"]
    colors = th["cta_badge_colors"]
    items = []
    for i, item in enumerate(s.get("items", [])):
        title = item if isinstance(item, str) else item.get("title", "")
        desc  = "" if isinstance(item, str) else item.get("description", "")
        items.append({
            "badge_color": colors[i % len(colors)],
            "title": title,
            "description": desc,
            "text_color": "FFFFFF",
        })
    return {
        "bg": _grad(bg["from"], bg["to"], ANG_BTM_TOP),
        "heading": s.get("heading", "Next Steps"),
        "heading_color": "FFFFFF",
        "items": items,
        "divider_color": "FFFFFF",
        "decor_color": th["cta_decor_color"],
    }


def _toc(s: dict, th: dict) -> dict:
    def _toc_items(raw: list, badge_color: str) -> list[dict]:
        result = []
        for item in raw:
            if isinstance(item, str):
                result.append({"section_title": item, "slide_range": "",
                                "badge_color": badge_color,
                                "title_color": th["title_color"],
                                "range_color": th["muted_color"]})
            else:
                result.append({
                    "section_title": item.get("section_title", item.get("label", "")),
                    "slide_range":   item.get("slide_range", ""),
                    "badge_color":   badge_color,
                    "title_color":   th["title_color"],
                    "range_color":   th["muted_color"],
                })
        return result

    sec0 = _sec(th, 0)
    sec1 = _sec(th, 1)
    return {
        "title": s.get("title", "Agenda"),
        "title_color": th["title_color"],
        "bg": _grad(th["slide_bg"]["from"], th["slide_bg"]["to"], ANG_TOP_BOTTOM),
        "accent_bar": _grad(th["accent_bar"]["from"], th["accent_bar"]["to"], ANG_LEFT_RIGHT),
        "separator_color": th["separator_color"],
        "left_items":  _toc_items(s.get("left_items", []),  sec0["badge"]),
        "right_items": _toc_items(s.get("right_items", []), sec1["badge"]),
    }


def _timeline(s: dict, th: dict) -> dict:
    d = _common(s, th)
    d["spine"] = _grad(th["accent_bar"]["from"], th["accent_bar"]["to"], ANG_LEFT_RIGHT)
    events = []
    for i, ev in enumerate(s.get("events", [])):
        t = _tint(th, i)
        border = t["border"]
        events.append({
            "date":        ev.get("date", ""),
            "label":       ev.get("label", ""),
            "description": ev.get("description", ""),
            "tint":        _tint_key(i),
            "bg":          _grad(t["bg_from"], t["bg_to"]),
            "dot_color":   border,
            "text_color":  th["body_color"],
            "date_color":  th["muted_color"],
        })
    d["events"] = events
    return d


def _icon_grid(s: dict, th: dict) -> dict:
    d = _common(s, th)
    d["n_cols"] = s.get("n_cols", 3)
    cells = []
    for i, cell in enumerate(s.get("cells", [])):
        t = _tint(th, i)
        border = t["border"]
        cells.append({
            "tint": _tint_key(i),
            "bg": _grad(t["bg_from"], t["bg_to"]),
            "border_top": border,
            "icon": {"type": cell.get("icon_type", "default"), "stroke": border, "size_pt": 36},
            "label": cell.get("label", ""),
            "label_color": th["title_color"],
            "sub_label": cell.get("sub_label", ""),
            "sub_label_color": th["muted_color"],
        })
    d["cells"] = cells
    return d


def _quote(s: dict, th: dict) -> dict:
    d = _common(s, th)
    badge_color = _sec(th, s.get("section_idx", 0))["badge"]
    d["accent_block_left"] = _grad(th["accent_bar"]["from"], th["accent_bar"]["to"], ANG_VERTICAL)
    d["quote_mark_color"]  = badge_color
    d["quote_text"]        = s.get("quote_text", "")
    d["quote_color"]       = th["title_color"]
    d["attribution"]       = s.get("attribution", "")
    d["attribution_color"] = th["muted_color"]
    d["context_text"]      = s.get("context_text", "")
    d["context_bg"]        = _grad(th["slide_bg"]["to"], th["slide_bg"]["from"])
    d["context_text_color"]= th["body_color"]
    return d


_RESOLVERS = {
    "I": _cover,
    "A": _card_grid,
    "B": _two_col_list,
    "C": _flow_steps,
    "D": _two_col_contrast,
    "E": _data_highlight,
    "F": _narrative,
    "G": _section_divider,
    "H": _cta,
    "J": _toc,
    "K": _timeline,
    "L": _icon_grid,
    "M": _quote,
}


# ── Public API ────────────────────────────────────────────────────────────────

def resolve_slide(slide: dict, th: dict) -> dict:
    """Return slide with "design" key populated.  Pass-through if already resolved."""
    if "design" in slide:
        return slide
    resolver = _RESOLVERS.get(slide.get("layout"))
    if resolver is None:
        raise ValueError(f"Unknown layout: {slide.get('layout')!r}")
    return {**slide, "design": resolver(slide, th)}


def resolve_deck(deck: dict) -> dict:
    """Resolve all slides in a deck; returns a new dict with design keys added."""
    theme_name = deck.get("deck_meta", {}).get("theme", "VTI")
    th = _THEMES.get(theme_name, _THEMES["VTI"])
    return {**deck, "slides": [resolve_slide(s, th) for s in deck.get("slides", [])]}
