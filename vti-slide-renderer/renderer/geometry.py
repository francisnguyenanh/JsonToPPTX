# geometry.py — Single source of truth for all EMU coordinates
# Canvas: 1280×720pt (Kimi AI standard, 16:9)
# No other module may hardcode EMU values; use pt() or constants from here.

# ── Slide dimensions ──────────────────────────────────────────────────
SLIDE_W = 16256000   # 1280pt × 12700
SLIDE_H = 9144000    # 720pt × 12700
PT      = 12700      # 1pt in EMU


def pt(n: float) -> int:
    """Convert points to EMU. Use everywhere instead of raw numbers."""
    return int(n * PT)


# ── Content Zone Budget ───────────────────────────────────────────────
MARGIN_X        = pt(27)
CONTENT_X       = pt(27)
CONTENT_W       = pt(1226)  # SLIDE_W - 2 × MARGIN_X
ACCENT_BAR_Y    = pt(113)
ACCENT_BAR_H    = pt(5)
CONTENT_TOP     = pt(140)
CONTENT_BOTTOM  = pt(640)
CONTENT_H       = pt(500)   # CONTENT_BOTTOM - CONTENT_TOP
FOOTER_Y        = pt(669)
CARD_GAP        = pt(13)
COL_GAP         = pt(13)

# ── Stretch-to-fill formulas ──────────────────────────────────────────

def card_h(n_rows: int) -> int:
    """Dynamic card height that always fills CONTENT_H."""
    return (CONTENT_H - CARD_GAP * (n_rows - 1)) // n_rows


def card_y(row_idx: int, n_rows: int) -> int:
    return CONTENT_TOP + row_idx * (card_h(n_rows) + CARD_GAP)


def card_w(n_cols: int) -> int:
    return (CONTENT_W - COL_GAP * (n_cols - 1)) // n_cols


def card_x(col_idx: int, n_cols: int) -> int:
    return CONTENT_X + col_idx * (card_w(n_cols) + COL_GAP)


# ── Footer fixed positions ────────────────────────────────────────────
FOOTER_NUM_X    = 605119
FOOTER_NUM_Y    = 8500533
FOOTER_NUM_W    = 711200
FOOTER_NUM_H    = 584735
FOOTER_COPY_X   = 1422400
FOOTER_COPY_Y   = 8550667
FOOTER_COPY_W   = 4233333
FOOTER_COPY_H   = 457200

# ── bodyPr inset constants ────────────────────────────────────────────
INS_CARD   = dict(lIns=pt(16), rIns=pt(16), tIns=pt(12), bIns=pt(12))
INS_HEADER = dict(lIns=pt(16), rIns=pt(16), tIns=pt(8),  bIns=pt(8))
INS_FOOTER = dict(lIns=pt(8),  rIns=pt(8),  tIns=0,      bIns=0)
INS_NONE   = dict(lIns=0,      rIns=0,      tIns=0,      bIns=0)

# ── Typography — standard sizes (pt) ─────────────────────────────────
FONT_SECTION_TITLE = 69   # Layout G section title
FONT_TITLE         = 40   # slide title
FONT_CARD_HEADER   = 26   # card/step header
FONT_HEADER        = 26   # alias for FONT_CARD_HEADER
FONT_BODY          = 17   # body/bullet text
FONT_SMALL         = 14   # breadcrumb/small text
FONT_BADGE         = 22   # badge number text
FONT_STAT_BIG      = 72   # large KPI / stat number
FONT_STAT_LABEL    = 17   # stat label below number
FONT_CTA_HEADING   = 40   # CTA/Next Steps heading
FONT_COVER_TITLE   = 56   # cover main title
FONT_COVER_SUB     = 32   # cover subtitle

# ── Standard font ────────────────────────────────────────────────────
FONT_NAME = "Calibri"
