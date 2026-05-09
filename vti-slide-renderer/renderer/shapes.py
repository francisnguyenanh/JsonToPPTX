# shapes.py  ECore shape builders using python-pptx + lxml OOXML injection
from __future__ import annotations

from lxml import etree
from pptx.util import Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn, nsmap

from . import geometry as G


# ── Helper: parse hex color ───────────────────────────────────────────

def _rgb(hex6: str) -> RGBColor:
    h = hex6.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _hex_upper(hex6: str) -> str:
    return hex6.lstrip("#").upper()


# ── Gradient fill via OOXML ───────────────────────────────────────────

def add_gradient_fill(shape, from_hex: str, to_hex: str, angle_emu: int, stops=None):
    """
    Apply gradient fill to any shape via OOXML injection.
    stops: optional list of (position_0_to_100000, hex) for multi-stop gradients.
    """
    spPr = shape.fill._xPr  # sp element for shapes; works for shapes
    # Remove any existing fill
    for tag in (qn("a:noFill"), qn("a:solidFill"), qn("a:gradFill"),
                qn("a:pattFill"), qn("a:blipFill")):
        for el in spPr.findall(tag):
            spPr.remove(el)

    gradFill = etree.SubElement(spPr, qn("a:gradFill"))
    gsLst = etree.SubElement(gradFill, qn("a:gsLst"))

    if stops is None:
        stops = [(0, from_hex), (100000, to_hex)]

    for pos, hex_color in stops:
        gs = etree.SubElement(gsLst, qn("a:gs"), pos=str(pos))
        srgbClr = etree.SubElement(gs, qn("a:srgbClr"), val=_hex_upper(hex_color))

    lin = etree.SubElement(gradFill, qn("a:lin"), ang=str(angle_emu), scaled="0")
    return gradFill


def _set_gradient_fill_on_spPr(spPr, from_hex: str, to_hex: str, angle_emu: int, stops=None):
    """Apply gradient fill directly on an spPr element (for shapes without .fill)."""
    for tag in (qn("a:noFill"), qn("a:solidFill"), qn("a:gradFill"),
                qn("a:pattFill"), qn("a:blipFill")):
        for el in spPr.findall(tag):
            spPr.remove(el)

    gradFill = etree.SubElement(spPr, qn("a:gradFill"))
    gsLst = etree.SubElement(gradFill, qn("a:gsLst"))

    if stops is None:
        stops = [(0, from_hex), (100000, to_hex)]

    for pos, hex_color in stops:
        gs = etree.SubElement(gsLst, qn("a:gs"), pos=str(pos))
        etree.SubElement(gs, qn("a:srgbClr"), val=_hex_upper(hex_color))

    etree.SubElement(gradFill, qn("a:lin"), ang=str(angle_emu), scaled="0")


def _set_solid_fill_on_spPr(spPr, hex_color: str, alpha: int = None):
    """Apply solid fill on spPr element. alpha: 0-100000 (100000=opaque)."""
    for tag in (qn("a:noFill"), qn("a:solidFill"), qn("a:gradFill"),
                qn("a:pattFill"), qn("a:blipFill")):
        for el in spPr.findall(tag):
            spPr.remove(el)
    solidFill = etree.SubElement(spPr, qn("a:solidFill"))
    srgbClr = etree.SubElement(solidFill, qn("a:srgbClr"), val=_hex_upper(hex_color))
    if alpha is not None:
        etree.SubElement(srgbClr, qn("a:alpha"), val=str(alpha))


# ── Rounded rectangle ────────────────────────────────────────────────

def add_rounded_rect(slide, x: int, y: int, w: int, h: int,
                     from_hex: str, to_hex: str,
                     angle_emu: int = 16200000,
                     border_hex: str = None, border_w_pt: float = 0):
    """
    Add roundRect shape (adj=16667 ≁Ecorner radius 13%).
    Optional top border as separate thin rect if border_hex provided.
    Returns the shape object.
    """
    from pptx.util import Emu as _Emu
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.ROUNDED_RECTANGLE = freeform; use preset
        _Emu(x), _Emu(y), _Emu(w), _Emu(h)
    )

    # Set preset geometry to roundRect
    spPr = shape._element.spPr  # noqa
    prstGeom = spPr.find(qn("a:prstGeom"))
    if prstGeom is not None:
        prstGeom.set("prst", "roundRect")
        avLst = prstGeom.find(qn("a:avLst"))
        if avLst is None:
            avLst = etree.SubElement(prstGeom, qn("a:avLst"))
        else:
            for gd in avLst.findall(qn("a:gd")):
                avLst.remove(gd)
        etree.SubElement(avLst, qn("a:gd"), name="adj", fmla="val 16667")

    # Remove line (border)
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        spPr.remove(ln)
    ln_el = etree.SubElement(spPr, qn("a:ln"))
    etree.SubElement(ln_el, qn("a:noFill"))

    # Gradient fill
    _set_gradient_fill_on_spPr(spPr, from_hex, to_hex, angle_emu)

    # Optional top border line
    if border_hex:
        bw = G.pt(border_w_pt) if border_w_pt else G.pt(3)
        border = slide.shapes.add_shape(1, _Emu(x), _Emu(y), _Emu(w), _Emu(bw))
        b_spPr = border._element.spPr
        _set_solid_fill_on_spPr(b_spPr, border_hex)
        b_ln = b_spPr.find(qn("a:ln"))
        if b_ln is not None:
            b_spPr.remove(b_ln)
        etree.SubElement(b_spPr, qn("a:ln")).append(
            etree.fromstring('<a:noFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
        )
        prstGeomB = b_spPr.find(qn("a:prstGeom"))
        if prstGeomB is not None:
            prstGeomB.set("prst", "rect")

    return shape


# ── Styled textbox ────────────────────────────────────────────────────

def add_textbox_styled(slide, x: int, y: int, w: int, h: int,
                       text: str,
                       font_name: str = G.FONT_NAME,
                       size_pt: float = G.FONT_BODY,
                       color_hex: str = "000000",
                       bold: bool = False,
                       italic: bool = False,
                       align: str = "left",
                       v_anchor: str = "t",
                       wrap: bool = True,
                       inset: dict = None,
                       autofit: str = "norm",
                       line_spacing: float = None,
                       lang: str = "vi-VN"):
    """
    Add textbox with full bodyPr set explicitly.
    Never leaves <a:bodyPr/> empty.
    """
    from pptx.util import Emu as _Emu
    txBox = slide.shapes.add_textbox(_Emu(x), _Emu(y), _Emu(w), _Emu(h))
    tf = txBox.text_frame

    # Build bodyPr attributes
    ins = inset if inset else G.INS_NONE
    wrap_val = "square" if wrap else "none"
    anchor_map = {"t": "t", "m": "ctr", "b": "b", "ctr": "ctr"}
    anchor_val = anchor_map.get(v_anchor, "t")

    bodyPr = tf._txBody.find(qn("a:bodyPr"))
    bodyPr.set("wrap", wrap_val)
    bodyPr.set("lIns", str(ins.get("lIns", 0)))
    bodyPr.set("rIns", str(ins.get("rIns", 0)))
    bodyPr.set("tIns", str(ins.get("tIns", 0)))
    bodyPr.set("bIns", str(ins.get("bIns", 0)))
    bodyPr.set("anchor", anchor_val)
    bodyPr.set("anchorCtr", "0")

    # Remove existing autofit children
    for tag in (qn("a:normAutofit"), qn("a:noAutofit"), qn("a:spAutoFit")):
        for el in bodyPr.findall(tag):
            bodyPr.remove(el)

    if autofit == "norm":
        etree.SubElement(bodyPr, qn("a:normAutofit"))
    elif autofit == "sp":
        etree.SubElement(bodyPr, qn("a:spAutoFit"))
    else:
        etree.SubElement(bodyPr, qn("a:noAutofit"))

    # Paragraph
    tf.word_wrap = wrap
    p = tf.paragraphs[0]

    # Alignment
    align_map = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
                 "right": PP_ALIGN.RIGHT, "justify": PP_ALIGN.JUSTIFY}
    p.alignment = align_map.get(align, PP_ALIGN.LEFT)

    if line_spacing:
        from pptx.util import Pt as _Pt
        from pptx.oxml.ns import qn as _qn
        pPr = p._pPr
        if pPr is None:
            pPr = etree.SubElement(p._p, qn("a:pPr"))
        lnSpc = etree.SubElement(pPr, qn("a:lnSpc"))
        spcPts = etree.SubElement(lnSpc, qn("a:spcPts"))
        spcPts.set("val", str(int(line_spacing * 100)))

    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.color.rgb = _rgb(color_hex)
    run.font.bold = bold
    run.font.italic = italic

    # Language
    rPr = run._r.find(qn("a:rPr"))
    if rPr is None:
        rPr = run._r.find(qn("a:rPr"))
    if rPr is not None:
        rPr.set("lang", lang)

    return txBox


# ── Badge (circular ellipse) ──────────────────────────────────────────

def add_badge(slide, x: int, y: int, number_or_text: str,
              bg_hex: str, text_hex: str = "FFFFFF", size_pt: float = 40):
    """Circular badge (ellipse) with centered number/text."""
    from pptx.util import Emu as _Emu
    sz = G.pt(size_pt)
    shape = slide.shapes.add_shape(9, _Emu(x), _Emu(y), _Emu(sz), _Emu(sz))  # 9 = oval

    spPr = shape._element.spPr
    _set_solid_fill_on_spPr(spPr, bg_hex)
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        spPr.remove(ln)
    etree.SubElement(spPr, qn("a:ln")).append(
        etree.fromstring('<a:noFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
    )

    tf = shape.text_frame
    tf.word_wrap = False
    bodyPr = tf._txBody.find(qn("a:bodyPr"))
    bodyPr.set("anchor", "ctr")
    bodyPr.set("anchorCtr", "1")
    bodyPr.set("lIns", "0")
    bodyPr.set("rIns", "0")
    bodyPr.set("tIns", "0")
    bodyPr.set("bIns", "0")

    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = str(number_or_text)
    run.font.name = G.FONT_NAME
    run.font.size = Pt(size_pt * 0.4)
    run.font.color.rgb = _rgb(text_hex)
    run.font.bold = True

    return shape


# ── Dot bullet ────────────────────────────────────────────────────────

def add_dot_bullet(slide, x: int, y: int, dot_hex: str, size_pt: float = 6):
    """Small filled circle for bullet points."""
    from pptx.util import Emu as _Emu
    sz = G.pt(size_pt)
    shape = slide.shapes.add_shape(9, _Emu(x), _Emu(y), _Emu(sz), _Emu(sz))
    spPr = shape._element.spPr
    _set_solid_fill_on_spPr(spPr, dot_hex)
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        spPr.remove(ln)
    etree.SubElement(spPr, qn("a:ln")).append(
        etree.fromstring('<a:noFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
    )
    # Remove text frame content
    shape.text_frame.text = ""
    return shape


# ── Separator line ────────────────────────────────────────────────────

def add_separator_line(slide, x: int, y: int, w: int, h: int, color_hex: str):
    """Thin rect used as horizontal or vertical separator."""
    from pptx.util import Emu as _Emu
    shape = slide.shapes.add_shape(1, _Emu(x), _Emu(y), _Emu(w), _Emu(h))
    spPr = shape._element.spPr
    _set_solid_fill_on_spPr(spPr, color_hex)
    ln = spPr.find(qn("a:ln"))
    if ln is not None:
        spPr.remove(ln)
    etree.SubElement(spPr, qn("a:ln")).append(
        etree.fromstring('<a:noFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
    )
    shape.text_frame.text = ""
    return shape


# ── Semantic icon (OOXML primitives only) ─────────────────────────────

def add_semantic_icon(slide, x: int, y: int, size_pt: float,
                      stroke_hex: str, icon_type: str):
    """
    OOXML geometric icon  Estroke-only, no bitmap, no PIL, no base64.
    Returns list of shapes added.
    """
    from pptx.util import Emu as _Emu

    sz = G.pt(size_pt)
    stroke_w_emu = G.pt(2.0) if size_pt >= 80 else G.pt(1.5)
    shapes_added = []

    def _add_stroke_shape(preset, sx, sy, sw, sh, rx=None, ry=None, rw=None, rh=None):
        """Add stroke-only shape at absolute coords."""
        s = slide.shapes.add_shape(1, _Emu(sx), _Emu(sy), _Emu(sw), _Emu(sh))
        spPr = s._element.spPr
        pg = spPr.find(qn("a:prstGeom"))
        if pg is not None:
            pg.set("prst", preset)
            avLst = pg.find(qn("a:avLst"))
            if avLst is None:
                avLst = etree.SubElement(pg, qn("a:avLst"))

        # No fill
        for tag in (qn("a:noFill"), qn("a:solidFill"), qn("a:gradFill")):
            for el in spPr.findall(tag):
                spPr.remove(el)
        etree.SubElement(spPr, qn("a:noFill"))

        # Stroke
        ln = spPr.find(qn("a:ln"))
        if ln is not None:
            spPr.remove(ln)
        ln_el = etree.SubElement(spPr, qn("a:ln"), w=str(stroke_w_emu))
        solidFill = etree.SubElement(ln_el, qn("a:solidFill"))
        etree.SubElement(solidFill, qn("a:srgbClr"), val=_hex_upper(stroke_hex))

        s.text_frame.text = ""
        shapes_added.append(s)
        return s

    cx, cy = x + sz // 8, y + sz // 8
    inner = sz * 3 // 4

    if icon_type == "ai":
        # Outer circle
        _add_stroke_shape("ellipse", x, y, sz, sz)
        # Inner circle
        off = sz // 4
        _add_stroke_shape("ellipse", x + off, y + off, sz // 2, sz // 2)
        # Dot at center (solid)
        dot_sz = G.pt(4) if size_pt >= 80 else G.pt(3)
        dot = slide.shapes.add_shape(9, _Emu(x + sz // 2 - dot_sz // 2),
                                     _Emu(y + sz // 2 - dot_sz // 2),
                                     _Emu(dot_sz), _Emu(dot_sz))
        d_spPr = dot._element.spPr
        _set_solid_fill_on_spPr(d_spPr, stroke_hex)
        d_ln = d_spPr.find(qn("a:ln"))
        if d_ln is not None:
            d_spPr.remove(d_ln)
        etree.SubElement(d_spPr, qn("a:ln")).append(
            etree.fromstring('<a:noFill xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
        )
        dot.text_frame.text = ""
        shapes_added.append(dot)

    elif icon_type == "settings":
        # Outer circle
        _add_stroke_shape("ellipse", x, y, sz, sz)
        # Inner gear-like ring
        off = sz // 5
        _add_stroke_shape("ellipse", x + off, y + off, sz - 2 * off, sz - 2 * off)

    elif icon_type == "data":
        # Bar chart: 3 vertical bars
        bar_w = sz // 5
        heights = [sz // 2, sz * 3 // 4, sz // 3]
        for i, bh in enumerate(heights):
            bx = x + i * (bar_w + G.pt(2))
            by = y + sz - bh
            _add_stroke_shape("rect", bx, by, bar_w, bh)

    elif icon_type == "flow":
        # Rounded rect
        _add_stroke_shape("roundRect", x + G.pt(4), y + sz // 3, sz - G.pt(8), sz // 3)
        # Arrow line (as thin rect)
        _add_stroke_shape("rect", x + sz // 2, y + sz // 6, G.pt(1), sz * 2 // 3)

    elif icon_type == "doc":
        # Document shape
        _add_stroke_shape("rect", x + G.pt(4), y, sz - G.pt(8), sz)
        # Lines inside
        off = sz // 5
        _add_stroke_shape("rect", x + G.pt(8), y + off * 2, sz - G.pt(16), G.pt(1))
        _add_stroke_shape("rect", x + G.pt(8), y + off * 3, sz - G.pt(16), G.pt(1))

    elif icon_type == "team":
        # Two circles (people)
        head_sz = sz // 3
        _add_stroke_shape("ellipse", x + sz // 8, y, head_sz, head_sz)
        _add_stroke_shape("ellipse", x + sz // 2, y, head_sz, head_sz)
        # Bodies
        _add_stroke_shape("roundRect", x, y + head_sz + G.pt(2), sz // 2, sz // 2)
        _add_stroke_shape("roundRect", x + sz // 2, y + head_sz + G.pt(2), sz // 2, sz // 2)

    elif icon_type == "check":
        # Circle with checkmark (two lines as rects)
        _add_stroke_shape("ellipse", x, y, sz, sz)
        # Check tick (approximate with small rect diagonal)
        _add_stroke_shape("rect", x + sz // 4, y + sz // 2, sz // 4, G.pt(1.5))
        _add_stroke_shape("rect", x + sz // 3, y + sz // 3, G.pt(1.5), sz // 2)

    elif icon_type == "chart":
        # Line chart (two line segments)
        _add_stroke_shape("ellipse", x, y + sz // 2, sz, G.pt(1.5))
        _add_stroke_shape("rect", x + G.pt(2), y + sz // 4, sz // 2, sz // 4)
        _add_stroke_shape("rect", x + sz // 2, y + sz // 8, sz // 3, sz // 4)

    elif icon_type == "lock":
        # Lock body
        _add_stroke_shape("roundRect", x + sz // 6, y + sz // 3, sz * 2 // 3, sz * 2 // 3)
        # Shackle (arc as ellipse top half)
        _add_stroke_shape("ellipse", x + sz // 4, y, sz // 2, sz // 2)

    elif icon_type == "star":
        # Pentagon approximation  Ejust ellipse + inner ellipse
        _add_stroke_shape("ellipse", x, y, sz, sz)
        off = sz // 4
        _add_stroke_shape("ellipse", x + off, y + off, sz // 2, sz // 2)

    else:  # default  Esingle ellipse
        _add_stroke_shape("ellipse", x, y, sz, sz)

    return shapes_added
