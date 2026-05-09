# tests/test_geometry.py
import pytest
from renderer.geometry import (
    pt, PT, SLIDE_W, SLIDE_H,
    card_h, card_y, card_w, card_x,
    CONTENT_W, CONTENT_H, CONTENT_TOP, CARD_GAP, COL_GAP,
    FOOTER_NUM_X, FOOTER_NUM_Y, FOOTER_COPY_X, FOOTER_COPY_Y
)


def test_pt_converts_correctly():
    assert pt(1) == 12700
    assert pt(10) == 127000
    assert pt(0) == 0


def test_slide_dimensions():
    assert SLIDE_W == 12192000
    assert SLIDE_H == 6858000


def test_card_h_fills_content_h():
    for n in range(1, 5):
        total = card_h(n) * n + CARD_GAP * (n - 1)
        assert abs(total - CONTENT_H) <= n, f"n={n}: total={total} != CONTENT_H={CONTENT_H}"


def test_card_w_fills_content_w():
    for n in range(1, 5):
        total = card_w(n) * n + COL_GAP * (n - 1)
        assert abs(total - CONTENT_W) <= n, f"n={n}: total={total} != CONTENT_W={CONTENT_W}"


def test_card_y_starts_at_content_top():
    assert card_y(0, 1) == CONTENT_TOP
    assert card_y(0, 3) == CONTENT_TOP


def test_card_x_starts_at_content_x():
    from renderer.geometry import CONTENT_X
    assert card_x(0, 1) == CONTENT_X
    assert card_x(0, 3) == CONTENT_X


def test_footer_positions_are_fixed():
    # These must never change
    assert FOOTER_NUM_X == 453839
    assert FOOTER_NUM_Y == 6375400
    assert FOOTER_COPY_X == 1066800
    assert FOOTER_COPY_Y == 6413000
