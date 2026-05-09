# layouts/toc.py — Layout J
from __future__ import annotations

from pptx.util import Emu
from .. import geometry as G
from ..shapes import add_textbox_styled, add_badge, add_separator_line
from ..footer import inject_footer
from ._common import add_slide_bg, add_accent_bar, add_slide_header


def render(prs, slide_data: dict):
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    d = slide_data["design"]
    sn = slide_data["slide_number"]

    add_slide_bg(slide, d.get("bg", {"from": "FFFFFF", "to": "EEF4FB"}))
    add_accent_bar(slide, d.get("accent_bar", {"from": "2362B0", "to": "7FC236"}))
    add_slide_header(slide, d.get("title", "Table of Contents"), d.get("breadcrumb", ""))

    items = d.get("items", [])
    n = len(items)
    cols = 2 if n > 4 else 1
    col_w = G.card_w(cols)

    for i, item in enumerate(items):
        col = i % cols
        row = i // cols
        ix = G.card_x(col, cols)
        iy = G.CONTENT_TOP + row * G.pt(40)

        badge_color = item.get("badge_color", "2362B0")
        add_badge(slide, ix, iy, str(i + 1), badge_color, size_pt=14)

        add_textbox_styled(slide, ix + G.pt(20), iy, col_w - G.pt(22), G.pt(30),
                           item.get("label", ""), bold=True, size_pt=G.FONT_HEADER,
                           color_hex=item.get("text_color", "172759"),
                           v_anchor="m", inset=G.INS_NONE, autofit="none")

        if item.get("description"):
            add_textbox_styled(slide, ix + G.pt(20), iy + G.pt(20),
                               col_w - G.pt(22), G.pt(18),
                               item["description"], size_pt=G.FONT_SMALL,
                               color_hex=item.get("sub_color", "6A7FA0"),
                               v_anchor="t", inset=G.INS_NONE, autofit="none")

    inject_footer(slide, sn)
