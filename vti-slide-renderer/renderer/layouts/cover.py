# layouts/cover.py  ELayout I
from __future__ import annotations

from pptx.util import Emu, Pt
from lxml import etree
from pptx.oxml.ns import qn

from .. import geometry as G
from ..shapes import (
    add_gradient_fill, _set_gradient_fill_on_spPr, _set_solid_fill_on_spPr,
    add_textbox_styled, add_semantic_icon, add_separator_line
)
from ..footer import inject_footer


def render(prs, slide_data: dict):
    slide_layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(slide_layout)
    d = slide_data["design"]
    sn = slide_data["slide_number"]

    # ── Background gradient ──────────────────────────────────────────
    bg = d.get("bg", {})
    bg_shape = slide.shapes.add_shape(
        1, Emu(0), Emu(0), Emu(G.SLIDE_W), Emu(G.SLIDE_H)
    )
    spPr = bg_shape._element.spPr
    _set_gradient_fill_on_spPr(spPr, bg["from"], bg["to"], bg.get("angle", 9000000))
    _remove_line(spPr)
    bg_shape.text_frame.text = ""

    # ── Left vertical bar ────────────────────────────────────────────
    lb = d.get("left_bar", {})
    bar_w = G.pt(8)
    left_bar = slide.shapes.add_shape(1, Emu(0), Emu(0), Emu(bar_w), Emu(G.SLIDE_H))
    lb_spPr = left_bar._element.spPr
    _set_gradient_fill_on_spPr(lb_spPr, lb["from"], lb["to"], 18000000)
    _remove_line(lb_spPr)
    left_bar.text_frame.text = ""

    # ── Right decorative strip ───────────────────────────────────────
    rs = d.get("right_strip", {})
    strip_w = G.pt(60)
    strip_x = G.SLIDE_W - strip_w
    opacity = rs.get("opacity", 30)
    alpha_emu = int((100 - opacity) / 100 * 100000)
    right_strip = slide.shapes.add_shape(
        1, Emu(strip_x), Emu(0), Emu(strip_w), Emu(G.SLIDE_H)
    )
    rs_spPr = right_strip._element.spPr
    # gradient with alpha
    for tag in (qn("a:noFill"), qn("a:solidFill"), qn("a:gradFill")):
        for el in rs_spPr.findall(tag):
            rs_spPr.remove(el)
    gradFill = etree.SubElement(rs_spPr, qn("a:gradFill"))
    gsLst = etree.SubElement(gradFill, qn("a:gsLst"))
    for pos, hx in [(0, rs["from"]), (100000, rs["to"])]:
        gs = etree.SubElement(gsLst, qn("a:gs"), pos=str(pos))
        srgb = etree.SubElement(gs, qn("a:srgbClr"), val=hx.upper())
        etree.SubElement(srgb, qn("a:alpha"), val=str(alpha_emu))
    etree.SubElement(gradFill, qn("a:lin"), ang=str(rs.get("angle", 9000000)), scaled="0")
    _remove_line(rs_spPr)
    right_strip.text_frame.text = ""

    # ── Right card area ──────────────────────────────────────────────
    rc = d.get("right_card", {})
    card_x = G.SLIDE_W - strip_w - G.pt(220)
    card_y = G.pt(80)
    card_w = G.pt(200)
    card_h = G.pt(360)

    rc_shape = slide.shapes.add_shape(
        1, Emu(card_x), Emu(card_y), Emu(card_w), Emu(card_h)
    )
    rc_spPr = rc_shape._element.spPr
    # Soft white/transparent card
    _set_solid_fill_on_spPr(rc_spPr, "FFFFFF", alpha=15000)
    _remove_line(rc_spPr)
    rc_shape.text_frame.text = ""

    # Icon inside right card
    icon_def = rc.get("icon", {})
    if icon_def:
        icon_sz = icon_def.get("size_pt", 80)
        icon_x = card_x + (card_w - G.pt(icon_sz)) // 2
        icon_y = card_y + (card_h - G.pt(icon_sz)) // 2
        add_semantic_icon(slide, icon_x, icon_y, icon_sz,
                          icon_def.get("stroke", "4A9EE0"),
                          icon_def.get("type", "default"))

    # ── Divider bar ──────────────────────────────────────────────────
    div = d.get("divider_bar", {})
    div_x = G.pt(28)
    div_y = G.pt(240)
    div_w = G.pt(400)
    div_h = G.pt(4)
    div_shape = slide.shapes.add_shape(
        1, Emu(div_x), Emu(div_y), Emu(div_w), Emu(div_h)
    )
    div_spPr = div_shape._element.spPr
    _set_gradient_fill_on_spPr(div_spPr, div["from"], div["to"], 5400000)
    _remove_line(div_spPr)
    div_shape.text_frame.text = ""

    # ── Text content ─────────────────────────────────────────────────
    tx = G.pt(28)
    text_w = G.SLIDE_W - G.pt(240) - bar_w

    # Tag
    if d.get("tag"):
        add_textbox_styled(slide, tx, G.pt(170), text_w, G.pt(28),
                           d["tag"], bold=True,
                           size_pt=11, color_hex=d.get("tag_color", "2362B0"),
                           v_anchor="m", inset=G.INS_NONE, autofit="none")

    # Title
    add_textbox_styled(slide, tx, G.pt(200), text_w, G.pt(100),
                       d.get("title", ""), bold=True,
                       size_pt=G.FONT_COVER_TITLE,
                       color_hex=d.get("title_color", "172759"),
                       v_anchor="t", inset=G.INS_NONE, autofit="norm", wrap=True)

    # Subtitle
    if d.get("subtitle"):
        add_textbox_styled(slide, tx, G.pt(310), text_w, G.pt(40),
                           d["subtitle"], size_pt=G.FONT_COVER_SUB,
                           color_hex=d.get("subtitle_color", "172759"),
                           v_anchor="m", inset=G.INS_NONE, autofit="none")

    # Caption
    if d.get("caption"):
        add_textbox_styled(slide, tx, G.pt(360), text_w, G.pt(28),
                           d["caption"], size_pt=10,
                           color_hex=d.get("caption_color", "6A7FA0"),
                           v_anchor="m", inset=G.INS_NONE, autofit="none")

    inject_footer(slide, sn)


def _remove_line(spPr):
    from pptx.oxml.ns import qn
    from lxml import etree
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        spPr.remove(ln)
    etree.SubElement(spPr, qn("a:ln")).append(
        etree.fromstring(
            '<a:noFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>'
        )
    )
