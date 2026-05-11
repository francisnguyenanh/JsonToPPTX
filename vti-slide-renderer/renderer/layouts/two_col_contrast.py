# layouts/two_col_contrast.py — Layout D (Kimi-inspired header strip)
from __future__ import annotations

from .. import geometry as G
from ..shapes import (
    add_textbox_styled, add_rounded_rect, add_solid_roundrect,
    add_dot_bullet,
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

    col_w = G.card_w(2)
    pad = G.pt(21)
    strip_h = G.pt(72)
    strip_pad = G.pt(12)

    for col_idx, (new_key, old_key) in enumerate(
            (("left_card", "left_col"), ("right_card", "right_col"))):
        col = d.get(new_key) or d.get(old_key, {})
        cx = G.card_x(col_idx, 2)
        cy = G.CONTENT_TOP
        ch = G.CONTENT_H

        strip_color = col.get("border_top", "4A9EE0")
        card_body = col.get("card_body", "FCFDFD")

        # White column body with shadow
        add_rounded_rect(slide, cx, cy, col_w, ch,
                         card_body, card_body,
                         angle_emu=0, shadow=True)

        # Colored header strip
        add_solid_roundrect(slide, cx, cy, col_w, strip_h, strip_color)

        # Header text on strip (white)
        if col.get("header"):
            add_textbox_styled(slide, cx + pad, cy + strip_pad,
                               col_w - 2 * pad, strip_h - 2 * strip_pad,
                               col["header"], bold=True,
                               size_pt=G.FONT_CARD_HEADER,
                               color_hex="FFFFFF",
                               v_anchor="m", inset=G.INS_NONE,
                               autofit="norm", wrap=True)

        # Bullets below strip, vertically centered
        bullets = col.get("bullets", [])
        bullet_adv = G.pt(43)
        bullets_h = len(bullets) * bullet_adv
        avail_h = ch - strip_h - 2 * pad
        top_offset = max(0, (avail_h - bullets_h) // 2)
        cur_y = cy + strip_h + pad + top_offset

        inner_x = cx + pad
        inner_w = col_w - 2 * pad

        for bullet in bullets:
            dot_color = bullet.get("dot_color", strip_color)
            add_dot_bullet(slide, inner_x, cur_y + G.pt(8), dot_color, 8)
            add_textbox_styled(slide, inner_x + G.pt(19), cur_y,
                               inner_w - G.pt(19), G.pt(40),
                               bullet.get("text", ""),
                               size_pt=G.FONT_BODY,
                               color_hex=col.get("text_color", "1C2D4F"),
                               v_anchor="t", inset=G.INS_NONE,
                               autofit="norm", wrap=True)
            cur_y += bullet_adv

    inject_footer(slide, sn)
