"""Convert source-prepped.png into a self-typing gold/blue ASCII SVG (SMIL).
Usage: make_ascii_svg.py [prepped.png] [out.svg]   STATIC=1 emits a frozen frame."""
import os, sys
from PIL import Image, ImageFilter
import numpy as np

SRC = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "portrait-ascii.svg"
STATIC = os.environ.get("STATIC") == "1"

# the card is dark, so bright pixels get the dense glyphs and black prints nothing
RAMP = " .,:;-~=+*ox%#&@"   # dark (blank) -> bright (dense)
COLS = 104
CHAR_W, LINE_H, FONT = 5.4, 9.6, 9
PAD = 16
BG, BORDER = "#050608", "#2a2f3a"
# tone bands by brightness: deep blue for shadows, blue mids, gold skin, light-gold highlights
TONES = [(0.30, "#3b6fd4"), (0.52, "#6c9cf0"), (0.80, "#d4af37"), (1.01, "#f7dc8a")]

img = Image.open(SRC).convert("L")
w, h = img.size
rows = int(round(COLS * (h / w) * (CHAR_W / LINE_H)))
small = img.resize((COLS, rows), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=2))
a = np.asarray(small, dtype=float) / 255.0
mask = np.asarray(img.resize((COLS, rows), Image.BOX)) > 8   # subject coverage

def tone(v):
    return next(c for t, c in TONES if v < t)

lines = []   # per row: list of (start_col, text, color) runs
for r in range(rows):
    runs, cur = [], None
    for c in range(COLS):
        if not mask[r, c]:
            ch, col = " ", None
        else:
            v = a[r, c]
            ch = RAMP[max(1, min(len(RAMP) - 1, int(v * len(RAMP))))]
            col = tone(v)
        if ch == " ":
            cur = None
            continue
        if cur and cur[2] == col and cur[0] + len(cur[1]) == c:
            cur[1] += ch
        else:
            cur = [c, ch, col]
            runs.append(cur)
    lines.append(runs)

W = COLS * CHAR_W
H = rows * LINE_H
TOP = 30
SW, SH = W + 2 * PAD, H + TOP + PAD
ROW_DUR, STAGGER = 0.45, 0.06

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SW:.0f} {SH:.0f}" width="{SW:.0f}" height="{SH:.0f}" role="img" aria-label="ASCII portrait">',
       f'<rect x="0.5" y="0.5" width="{SW - 1:.0f}" height="{SH - 1:.0f}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
       '<circle cx="18" cy="15" r="4.5" fill="#d4af37"/><circle cx="34" cy="15" r="4.5" fill="#f7dc8a"/><circle cx="50" cy="15" r="4.5" fill="#3b82f6"/>',
       f'<text x="{SW / 2:.0f}" y="19" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11" fill="#8ba3c7">portrait.txt</text>']
if not STATIC:
    out.append('<defs>')
    for i in range(rows):
        y = TOP + i * LINE_H
        t0 = 0.3 + i * STAGGER
        out.append(f'<clipPath id="c{i}"><rect x="{PAD}" y="{y:.1f}" width="0" height="{LINE_H}">'
                   f'<animate attributeName="width" from="0" to="{W:.0f}" begin="{t0:.2f}s" dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>')
    out.append('</defs>')
out.append(f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FONT}" font-weight="bold" xml:space="preserve">')
for i, runs in enumerate(lines):
    if not runs:
        continue
    base = TOP + (i + 1) * LINE_H - 2.2
    clip = "" if STATIC else f' clip-path="url(#c{i})"'
    parts = [f'<text x="{PAD + c * CHAR_W:.1f}" y="{base:.1f}" fill="{col}" textLength="{len(t) * CHAR_W:.1f}" lengthAdjust="spacingAndGlyphs">{esc(t)}</text>'
             for c, t, col in runs]
    out.append(f'<g{clip}>{"".join(parts)}</g>')
out.append('</g>')
if not STATIC:
    # gold cursor block riding each wipe edge
    for i, runs in enumerate(lines):
        if not runs:
            continue
        y = TOP + i * LINE_H
        t0 = 0.3 + i * STAGGER
        end = PAD + (runs[-1][0] + len(runs[-1][1])) * CHAR_W
        out.append(f'<rect x="{PAD}" y="{y + 1:.1f}" width="{CHAR_W}" height="{LINE_H - 2}" fill="#f7dc8a" opacity="0">'
                   f'<animate attributeName="x" from="{PAD}" to="{end:.0f}" begin="{t0:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
                   f'<set attributeName="opacity" to="0.9" begin="{t0:.2f}s"/>'
                   f'<set attributeName="opacity" to="0" begin="{t0 + ROW_DUR:.2f}s"/></rect>')
out.append('</svg>')
open(OUT, "w", encoding="utf-8").write("\n".join(out))
print("wrote", OUT, f"{COLS}x{rows}", f"{SW:.0f}x{SH:.0f}")
