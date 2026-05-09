# engine.py — Render orchestrator
from __future__ import annotations

import io
from pptx import Presentation
from pptx.util import Emu

from . import geometry as G
from .validator import validate
from .layouts import (
    cover, card_grid, two_col_list, flow_steps, two_col_contrast,
    data_highlight, narrative, section_divider, cta, toc, timeline,
    icon_grid, quote
)

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


class ValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Validation failed")


def render_deck(deck_json: dict) -> bytes:
    """
    1. Validate JSON against schema — raise ValidationError if invalid
    2. Create Presentation with SLIDE_W × SLIDE_H
    3. For each slide: call LAYOUT_MAP[layout](prs, slide_data)
    4. Each layout calls inject_footer as its final step
    5. Save to BytesIO, return bytes
    """
    ok, errors = validate(deck_json)
    if not ok:
        raise ValidationError(errors)

    prs = Presentation()
    prs.slide_width = Emu(G.SLIDE_W)
    prs.slide_height = Emu(G.SLIDE_H)

    for slide_data in deck_json["slides"]:
        layout_key = slide_data["layout"]
        renderer = LAYOUT_MAP.get(layout_key)
        if renderer is None:
            raise ValueError(f"Unknown layout: {layout_key!r}")
        renderer(prs, slide_data)

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()
