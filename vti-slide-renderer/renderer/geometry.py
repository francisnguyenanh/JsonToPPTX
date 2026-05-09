# geometry.py — Single source of truth for all EMU coordinates
# No other module may hardcode EMU values; use pt() or constants from here.

# ── Slide dimensions ──────────────────────────────────────────────────
SLIDE_W = 12192000   # 960pt × 12700
SLIDE_H = 6858000    # 540pt × 12700
PT      = 12700      # 1pt in EMU


def pt(n: float) -> int:
    """Convert points to EMU. Use everywhere instead of raw numbers."""
    return int(n * PT)


# ── Content Zone Budget ───────────────────────────────────────────────
MARGIN_X        = pt(20)
CONTENT_X       = pt(20)
CONTENT_W       = pt(920)   # SLIDE_W - 2 × MARGIN_X
ACCENT_BAR_Y    = pt(85)
ACCENT_BAR_H    = pt(4)
CONTENT_TOP     = pt(105)
CONTENT_BOTTOM  = pt(480)
CONTENT_H       = pt(375)   # CONTENT_BOTTOM - CONTENT_TOP
FOOTER_Y        = pt(502)
CARD_GAP        = pt(10)
COL_GAP         = pt(10)

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
FOOTER_NUM_X    = 453839
FOOTER_NUM_Y    = 6375400
FOOTER_NUM_W    = 533400
FOOTER_NUM_H    = 438551
FOOTER_COPY_X   = 1066800
FOOTER_COPY_Y   = 6413000
FOOTER_COPY_W   = 3175000
FOOTER_COPY_H   = 342900

# ── bodyPr inset constants ────────────────────────────────────────────
INS_CARD   = dict(lIns=pt(12), rIns=pt(12), tIns=pt(9),  bIns=pt(9))
INS_HEADER = dict(lIns=pt(12), rIns=pt(12), tIns=pt(6),  bIns=pt(6))
INS_FOOTER = dict(lIns=pt(6),  rIns=pt(6),  tIns=0,      bIns=0)
INS_NONE   = dict(lIns=0,      rIns=0,      tIns=0,      bIns=0)

# ── Typography — standard sizes (pt) — aligned with VTI design system ─
FONT_SECTION_TITLE = 52   # Layout G section title (range 50–54)
FONT_TITLE         = 34   # slide title (range 32–36)
FONT_CARD_HEADER   = 22   # card/step header (range 20–24)
FONT_HEADER        = 22   # alias for FONT_CARD_HEADER
FONT_BODY          = 15   # body/bullet text (range 14–16, floor 14)
FONT_SMALL         = 13   # breadcrumb/small text (range 12–14)
FONT_BADGE         = 17   # badge number text (range 16–18)
FONT_STAT_BIG      = 60   # large KPI / stat number (range 56–64)
FONT_STAT_LABEL    = 15   # stat label below number (range 14–16)
FONT_CTA_HEADING   = 30   # CTA/Next Steps heading (range 28–32)
FONT_COVER_TITLE   = 68   # cover main title (range 64–72)
FONT_COVER_SUB     = 26   # cover subtitle (range 24–28)

# ── Standard font ────────────────────────────────────────────────────
FONT_NAME = "Arial"
