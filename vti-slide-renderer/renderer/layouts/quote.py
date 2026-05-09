# layouts/quote.py — Layout M
from __future__ import annotations

from pptx.util import Emu
from lxml import etree
from pptx.oxml.ns import qn

from .. import geometry as G
from ..shapes import (
    add_textbox_styled, add_separator_line,
    _set_gradient_fill_on_spPr, _set_solid_fill_on_spPr
)
from ..footer import inject_footer
from ._common import add_slide_bg, add_accent_bar, remove_line


def render(prs, slide_data: dict):
    slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(slide_layout)
    d = slide_data["design"]
    sn = slide_data["slide_number"]

    add_slide_bg(slide, d.get("bg", {"from": "FFFFFF", "to": "EEF4FB"}))
    add_accent_bar(slide, d.get("accent_bar", {"from": "2362B0", "to": "7FC236"}))

    # Decorative large quote mark
    quote_color = d.get("quote_mark_color", "EEF4FB")
    add_textbox_styled(slide, G.CONTENT_X, G.CONTENT_TOP - G.pt(20),
                       G.pt(80), G.pt(80), "\u201c",
                       size_pt=120, color_hex=quote_color,
                       bold=True, v_anchor="t", inset=G.INS_NONE, autofit="none")

    # Quote text
    add_textbox_styled(slide,
                       G.CONTENT_X + G.pt(40), G.CONTENT_TOP + G.pt(30),
                       G.CONTENT_W - G.pt(80),
                       G.CONTENT_H - G.pt(60),
                       d.get("quote", ""),
                       size_pt=20, bold=True,
                       color_hex=d.get("quote_color", "172759"),
                       align="center", v_anchor="m",
                       inset=G.INS_CARD, autofit="norm", wrap=True,
                       line_spacing=1.4)

    # Attribution
    if d.get("attribution"):
        add_textbox_styled(slide,
                           G.CONTENT_X, G.CONTENT_BOTTOM - G.pt(30),
                           G.CONTENT_W, G.pt(24),
                           "— " + d["attribution"],
                           size_pt=G.FONT_BODY,
                           color_hex=d.get("attribution_color", "6A7FA0"),
                           align="right", v_anchor="m",
                           inset=G.INS_NONE, autofit="none")

    inject_footer(slide, sn)
