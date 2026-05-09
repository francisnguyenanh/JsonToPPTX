# layouts/flow_steps.py — Layout C
from __future__ import annotations

from pptx.util import Emu
from .. import geometry as G
from ..shapes import add_textbox_styled, add_rounded_rect, add_badge, add_separator_line
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

    steps = d.get("steps", [])
    n = len(steps)
    direction = d.get("flow_direction", "horizontal")
    arrow_color = d.get("arrow_color", "B8D0EE")

    if direction == "horizontal":
        step_w = G.card_w(n)
        step_h = G.CONTENT_H
        for i, step in enumerate(steps):
            sx = G.card_x(i, n)
            sy = G.CONTENT_TOP
            bg = step.get("bg", {"from": "EBF4FC", "to": "D6EAF8"})
            add_rounded_rect(slide, sx, sy, step_w, step_h,
                             bg["from"], bg["to"],
                             border_hex=step.get("border_top"),
                             border_w_pt=3)

            # Arrow between steps
            if i < n - 1:
                arr_x = sx + step_w + G.pt(2)
                arr_y = sy + step_h // 2 - G.pt(1)
                add_separator_line(slide, arr_x, arr_y, G.COL_GAP - G.pt(4), G.pt(2), arrow_color)

            inner_x = sx + G.pt(12)
            inner_w = step_w - G.pt(24)
            cur_y = sy + G.pt(16)

            badge_color = step.get("badge_color", "2362B0")
            badge_label = str(i + 1)
            add_badge(slide, inner_x, cur_y, badge_label, badge_color, size_pt=14)
            cur_y += G.pt(20)

            if step.get("header"):
                add_textbox_styled(slide, inner_x, cur_y, inner_w, G.pt(24),
                                   step["header"], bold=True,
                                   size_pt=G.FONT_HEADER,
                                   color_hex=step.get("header_color", "172759"),
                                   v_anchor="t", inset=G.INS_NONE, autofit="none", wrap=True)
                cur_y += G.pt(28)

            if step.get("description"):
                add_textbox_styled(slide, inner_x, cur_y, inner_w,
                                   step_h - (cur_y - sy) - G.pt(12),
                                   step["description"],
                                   size_pt=G.FONT_BODY,
                                   color_hex=step.get("text_color", "1C2D4F"),
                                   v_anchor="t", inset=G.INS_NONE, autofit="norm", wrap=True)
    else:
        # Vertical flow
        step_h = G.card_h(n)
        for i, step in enumerate(steps):
            sx = G.CONTENT_X
            sy = G.card_y(i, n)
            bg = step.get("bg", {"from": "EBF4FC", "to": "D6EAF8"})
            add_rounded_rect(slide, sx, sy, G.CONTENT_W, step_h,
                             bg["from"], bg["to"],
                             border_hex=step.get("border_top"), border_w_pt=3)

            inner_x = sx + G.pt(12)
            cur_y = sy + G.pt(10)
            badge_color = step.get("badge_color", "2362B0")
            add_badge(slide, inner_x, cur_y, str(i + 1), badge_color, size_pt=14)

            if step.get("header"):
                add_textbox_styled(slide, inner_x + G.pt(20), cur_y,
                                   G.CONTENT_W - G.pt(40), G.pt(22),
                                   step["header"], bold=True,
                                   size_pt=G.FONT_HEADER,
                                   color_hex=step.get("header_color", "172759"),
                                   v_anchor="m", inset=G.INS_NONE, autofit="none")

    inject_footer(slide, sn)
