# layouts/narrative.py — Layout F
from __future__ import annotations

from pptx.util import Emu
from .. import geometry as G
from ..shapes import add_textbox_styled, add_rounded_rect, add_separator_line
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

    body_text = d.get("body", "")
    add_textbox_styled(
        slide,
        G.CONTENT_X, G.CONTENT_TOP, G.CONTENT_W, G.CONTENT_H,
        body_text,
        size_pt=G.FONT_BODY,
        color_hex=d.get("text_color", "1C2D4F"),
        v_anchor="t", inset=G.INS_CARD, autofit="norm", wrap=True,
        line_spacing=1.4
    )

    inject_footer(slide, sn)
