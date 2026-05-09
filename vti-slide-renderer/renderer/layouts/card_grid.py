# layouts/card_grid.py — Layout A
from __future__ import annotations

from pptx.util import Emu
from .. import geometry as G
from ..shapes import (
    add_textbox_styled, add_rounded_rect, add_dot_bullet,
    add_semantic_icon, _set_solid_fill_on_spPr
)
from ..footer import inject_footer
from ._common import add_slide_bg, add_accent_bar, add_slide_header, remove_line
from lxml import etree
from pptx.oxml.ns import qn


def render(prs, slide_data: dict):
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    d = slide_data["design"]
    sn = slide_data["slide_number"]

    add_slide_bg(slide, d.get("bg", {"from": "FFFFFF", "to": "EEF4FB"}))
    add_accent_bar(slide, d.get("accent_bar", {"from": "2362B0", "to": "7FC236"}))
    add_slide_header(slide, d.get("title", ""), d.get("breadcrumb", ""))

    cards = d.get("cards", [])
    n_cols = d.get("n_cols", len(cards))
    n_rows = 1

    for col_idx, card in enumerate(cards):
        cx = G.card_x(col_idx, n_cols)
        cy = G.card_y(0, n_rows)
        cw = G.card_w(n_cols)
        ch = G.card_h(n_rows)

        card_bg = card.get("bg", {"from": "EBF4FC", "to": "D6EAF8"})
        add_rounded_rect(slide, cx, cy, cw, ch,
                         card_bg["from"], card_bg["to"],
                         angle_emu=16200000,
                         border_hex=card.get("border_top"),
                         border_w_pt=3)

        inner_x = cx + G.pt(12)
        inner_w = cw - G.pt(24)
        cur_y = cy + G.pt(12)

        # Icon
        icon = card.get("icon")
        if icon:
            sz = icon.get("size_pt", 36)
            add_semantic_icon(slide, inner_x, cur_y, sz,
                              icon.get("stroke", "4A9EE0"),
                              icon.get("type", "default"))
            cur_y += G.pt(sz + 6)

        # Header
        if card.get("header"):
            add_textbox_styled(slide, inner_x, cur_y, inner_w, G.pt(24),
                               card["header"], bold=True,
                               size_pt=G.FONT_HEADER,
                               color_hex=card.get("header_color", "172759"),
                               v_anchor="t", inset=G.INS_NONE, autofit="none")
            cur_y += G.pt(28)

        # Bullets
        for bullet in card.get("bullets", []):
            dot_sz = G.pt(6)
            dot_y = cur_y + G.pt(3)
            from ..shapes import add_dot_bullet
            add_dot_bullet(slide, inner_x, dot_y, bullet.get("dot_color", "4A9EE0"), 6)
            add_textbox_styled(slide, inner_x + G.pt(12), cur_y,
                               inner_w - G.pt(12), G.pt(18),
                               bullet.get("text", ""),
                               size_pt=G.FONT_BODY,
                               color_hex=card.get("text_color", "1C2D4F"),
                               v_anchor="t", inset=G.INS_NONE, autofit="none", wrap=True)
            cur_y += G.pt(20)

    inject_footer(slide, sn)
