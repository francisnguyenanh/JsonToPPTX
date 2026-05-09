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

# ── Typography — standard sizes (pt) ──────────────────────────────────
FONT_TITLE      = 28
FONT_HEADER     = 14
FONT_BODY       = 10
FONT_SMALL      = 9
FONT_BADGE      = 11
FONT_COVER_TITLE = 36
FONT_COVER_SUB  = 14

# ── Standard font ────────────────────────────────────────────────────
FONT_NAME = "Arial"
