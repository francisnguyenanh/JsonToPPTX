# layouts/card_grid.py — Layout A (Kimi-inspired: white card + colored pill header + shadow)
from __future__ import annotations

from .. import geometry as G
from ..shapes import (
    add_textbox_styled, add_rounded_rect, add_solid_roundrect,
    add_dot_bullet, add_semantic_icon,
)
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

    cards = d.get("cards", [])
    n_cols = d.get("n_cols", len(cards))
    n_rows = 1

    # Adaptive sizing per column count
    if n_cols <= 2:
        header_font = 25;  body_font = 17
        strip_h = G.pt(77); strip_pad = G.pt(13)
        bullet_h = G.pt(37); bullet_adv = G.pt(40)
        icon_sz_default = 37; pad = G.pt(21)
    elif n_cols == 3:
        header_font = 21;  body_font = 16
        strip_h = G.pt(69); strip_pad = G.pt(11)
        bullet_h = G.pt(32); bullet_adv = G.pt(35)
        icon_sz_default = 32; pad = G.pt(19)
    else:  # 4 columns
        header_font = 18;  body_font = 14
        strip_h = G.pt(61); strip_pad = G.pt(9)
        bullet_h = G.pt(29); bullet_adv = G.pt(32)
        icon_sz_default = 27; pad = G.pt(16)

    for col_idx, card in enumerate(cards):
        cx = G.card_x(col_idx, n_cols)
        cy = G.card_y(0, n_rows)
        cw = G.card_w(n_cols)
        ch = G.card_h(n_rows)

        strip_color = card.get("border_top", "4A9EE0")
        card_body = card.get("card_body", "FCFDFD")

        # White card body with drop shadow
        add_rounded_rect(slide, cx, cy, cw, ch,
                         card_body, card_body,
                         angle_emu=0, shadow=True)

        # Colored pill-shaped header strip
        add_solid_roundrect(slide, cx, cy, cw, strip_h, strip_color)

        # Header text on strip (white, bold, vertically centered)
        if card.get("header"):
            add_textbox_styled(slide, cx + pad, cy + strip_pad,
                               cw - 2 * pad, strip_h - 2 * strip_pad,
                               card["header"], bold=True,
                               size_pt=header_font,
                               color_hex="FFFFFF",
                               v_anchor="m", inset=G.INS_NONE,
                               autofit="norm", wrap=True)

        # Content: icon + bullets, vertically centered in card body below strip
        inner_x = cx + pad
        inner_w = cw - 2 * pad
        bullets = card.get("bullets", [])
        icon = card.get("icon")
        icon_sz = icon.get("size_pt", icon_sz_default) if icon else 0
        icon_block = G.pt(icon_sz + 8) if icon_sz else 0
        bullets_block = len(bullets) * bullet_adv
        total_content = icon_block + bullets_block

        avail_h = ch - strip_h - 2 * pad
        top_offset = max(0, (avail_h - total_content) // 2)
        cur_y = cy + strip_h + pad + top_offset

        if icon:
            add_semantic_icon(slide, inner_x, cur_y, icon_sz,
                              strip_color, icon.get("type", "default"))
            cur_y += icon_block

        for bullet in bullets:
            dot_color = bullet.get("dot_color", strip_color)
            add_dot_bullet(slide, inner_x, cur_y + G.pt(7), dot_color, 7)
            add_textbox_styled(slide, inner_x + G.pt(17), cur_y,
                               inner_w - G.pt(17), bullet_h,
                               bullet.get("text", ""),
                               size_pt=body_font,
                               color_hex=card.get("text_color", "1C2D4F"),
                               v_anchor="t", inset=G.INS_NONE,
                               autofit="norm", wrap=True)
            cur_y += bullet_adv

    inject_footer(slide, sn)
