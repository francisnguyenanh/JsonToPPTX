# layouts/two_col_contrast.py — Layout D
from __future__ import annotations

from pptx.util import Emu
from .. import geometry as G
from ..shapes import add_textbox_styled, add_rounded_rect, add_dot_bullet
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

    col_w = G.card_w(2)
    for col_idx, col_key in enumerate(("left_col", "right_col")):
        col = d.get(col_key, {})
        cx = G.card_x(col_idx, 2)
        cy = G.CONTENT_TOP
        ch = G.CONTENT_H
        bg = col.get("bg", {"from": "EBF4FC", "to": "D6EAF8"})
        add_rounded_rect(slide, cx, cy, col_w, ch,
                         bg["from"], bg["to"],
                         border_hex=col.get("border_top"), border_w_pt=3)

        inner_x = cx + G.pt(12)
        inner_w = col_w - G.pt(24)
        cur_y = cy + G.pt(12)

        if col.get("header"):
            add_textbox_styled(slide, inner_x, cur_y, inner_w, G.pt(24),
                               col["header"], bold=True,
                               size_pt=G.FONT_HEADER,
                               color_hex=col.get("header_color", "172759"),
                               v_anchor="t", inset=G.INS_NONE, autofit="none")
            cur_y += G.pt(28)

        for bullet in col.get("bullets", []):
            add_dot_bullet(slide, inner_x, cur_y + G.pt(4),
                           bullet.get("dot_color", "4A9EE0"), 6)
            add_textbox_styled(slide, inner_x + G.pt(12), cur_y,
                               inner_w - G.pt(12), G.pt(18),
                               bullet.get("text", ""),
                               size_pt=G.FONT_BODY,
                               color_hex=col.get("text_color", "1C2D4F"),
                               v_anchor="t", inset=G.INS_NONE, autofit="none", wrap=True)
            cur_y += G.pt(22)

    inject_footer(slide, sn)
