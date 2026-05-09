# layouts/data_highlight.py — Layout E
from __future__ import annotations

from pptx.util import Emu
from .. import geometry as G
from ..shapes import add_textbox_styled, add_rounded_rect
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

    stats = d.get("stats", [])
    n = len(stats)

    # Stats area: top 2/3 of content zone
    stats_h = G.CONTENT_H * 2 // 3
    stat_w = G.card_w(n)

    for i, stat in enumerate(stats):
        sx = G.card_x(i, n)
        sy = G.CONTENT_TOP
        bg = stat.get("bg", {"from": "EBF4FC", "to": "D6EAF8"})
        add_rounded_rect(slide, sx, sy, stat_w, stats_h,
                         bg["from"], bg["to"])

        inner_x = sx + G.pt(12)
        inner_w = stat_w - G.pt(24)
        num_y = sy + G.pt(20)
        label_y = sy + stats_h - G.pt(40)

        add_textbox_styled(slide, inner_x, num_y, inner_w, G.pt(60),
                           stat.get("number", "") + stat.get("unit", ""),
                           bold=True, size_pt=36,
                           color_hex=stat.get("number_color", "2362B0"),
                           align="center", v_anchor="m",
                           inset=G.INS_NONE, autofit="none")

        add_textbox_styled(slide, inner_x, label_y, inner_w, G.pt(30),
                           stat.get("label", ""),
                           size_pt=G.FONT_BODY,
                           color_hex=stat.get("label_color", "6A7FA0"),
                           align="center", v_anchor="m",
                           inset=G.INS_NONE, autofit="none")

    # Context strip
    ctx = d.get("context_text", "")
    if ctx:
        ctx_y = G.CONTENT_TOP + stats_h + G.CARD_GAP
        ctx_h = G.CONTENT_H - stats_h - G.CARD_GAP
        ctx_bg = d.get("context_bg", {"from": "EEF4FB", "to": "FFFFFF"})
        add_rounded_rect(slide, G.CONTENT_X, ctx_y, G.CONTENT_W, ctx_h,
                         ctx_bg["from"], ctx_bg["to"])
        add_textbox_styled(slide, G.CONTENT_X + G.pt(12), ctx_y,
                           G.CONTENT_W - G.pt(24), ctx_h,
                           ctx,
                           size_pt=G.FONT_BODY,
                           color_hex=d.get("context_text_color", "1C2D4F"),
                           v_anchor="m", inset=G.INS_NONE, autofit="none", wrap=True)

    inject_footer(slide, sn)
