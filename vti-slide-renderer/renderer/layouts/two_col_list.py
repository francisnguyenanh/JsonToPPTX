# layouts/two_col_list.py — Layout B
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
    add_slide_header(slide, d.get("title", ""), d.get("breadcrumb", ""))

    col_w = (G.CONTENT_W - G.pt(1)) // 2
    left_x = G.CONTENT_X
    right_x = G.CONTENT_X + col_w + G.pt(1)

    # Vertical separator
    sep_color = d.get("separator_color", "B8D0EE")
    add_separator_line(slide, G.CONTENT_X + col_w, G.CONTENT_TOP,
                       G.pt(1), G.CONTENT_H, sep_color)

    def draw_items(items, start_x):
        cy = G.CONTENT_TOP + G.pt(8)
        for item in items:
            badge_color = item.get("badge_color", "2362B0")
            add_badge(slide, start_x, cy, "•", badge_color, size_pt=8)
            add_textbox_styled(slide, start_x + G.pt(14), cy,
                               col_w - G.pt(16), G.pt(20),
                               item.get("text", ""),
                               size_pt=G.FONT_BODY,
                               color_hex=item.get("text_color", "1C2D4F"),
                               v_anchor="m", inset=G.INS_NONE, autofit="none", wrap=True)
            cy += G.pt(24)

    draw_items(d.get("left_items", []), left_x)
    draw_items(d.get("right_items", []), right_x)

    inject_footer(slide, sn)
