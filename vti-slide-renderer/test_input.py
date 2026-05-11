"""Render output/input.json with all fixes applied."""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from renderer.engine import render_deck

with open("output/input.json", encoding="utf-8") as f:
    deck = json.load(f)

data = render_deck(deck)
out = "output/output_fixed.pptx"
with open(out, "wb") as f:
    f.write(data)
print(f"OK - {len(deck['slides'])} slides -> {out} ({len(data):,} bytes)")
