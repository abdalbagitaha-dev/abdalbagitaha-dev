"""Hand-authored neofetch-style info card (animated SVG). STATIC=1 emits a frozen frame."""
import os

STATIC = os.environ.get("STATIC") == "1"
W, H = 700, 450
BG, BORDER = "#0a1628", "#1e3a5f"
KEY, VAL, DIM, ACC = "#d4af37", "#e6edf3", "#8ba3c7", "#60a5fa"

USER = "abdalbagitaha-dev"
ROWS = [
    ("Role",     "Odoo Functional Consultant"),
    ("Odoo",     "v18 / v19"),
    ("Modules",  "Sales · Inventory · POS · Accounting · Purchases"),
    ("Edu",      "B.Sc. Information Technology, Jazan University (2025)"),
    ("Award",    "1st Place, Raqeem Accounting Hackathon 2024"),
    ("Location", "Saudi Arabia"),
    ("Status",   "Open to roles anywhere in KSA"),
]
SWATCH = ["#0f2340", "#1e3a8a", "#2563eb", "#60a5fa", "#8a6d1d", "#b8912f", "#d4af37", "#f7dc8a"]

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def appear(i, base=0.4, step=0.16):
    """fade + slide-in animation tags for the i-th line"""
    if STATIC:
        return ""
    t = base + i * step
    return (f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.35s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-10 0" to="0 0" begin="{t:.2f}s" dur="0.35s" fill="freeze"/>')

op = "1" if STATIC else "0"
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Profile info card">',
       f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
       '<circle cx="22" cy="20" r="5.5" fill="#d4af37"/><circle cx="42" cy="20" r="5.5" fill="#f7dc8a"/><circle cx="62" cy="20" r="5.5" fill="#3b82f6"/>',
       f'<text x="{W/2}" y="25" text-anchor="middle" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="13" fill="{DIM}">neofetch</text>',
       '<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="17" xml:space="preserve">']

y = 78
line = 0
out.append(f'<g opacity="{op}">{appear(line)}<text x="32" y="{y}"><tspan fill="{KEY}" font-weight="bold">{USER}</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{ACC}" font-weight="bold">github</tspan></text></g>')
y += 24; line += 1
out.append(f'<g opacity="{op}">{appear(line)}<text x="32" y="{y}" fill="{DIM}">{"-" * (len(USER) + 7)}</text></g>')
y += 38; line += 1
for k, v in ROWS:
    out.append(f'<g opacity="{op}">{appear(line)}<text x="32" y="{y}"><tspan fill="{KEY}" font-weight="bold">{esc(k)}</tspan><tspan fill="{DIM}">: </tspan><tspan fill="{VAL}">{esc(v)}</tspan></text></g>')
    y += 36; line += 1
# colour swatches like neofetch
y += 8
sw = []
for i, c in enumerate(SWATCH):
    sw.append(f'<rect x="{32 + i * 34}" y="{y}" width="28" height="18" rx="3" fill="{c}"/>')
out.append(f'<g opacity="{op}">{appear(line)}{"".join(sw)}</g>')
out.append('</g></svg>')
dest = "info-card-static.svg" if STATIC else "info-card.svg"
open(dest, "w", encoding="utf-8").write("\n".join(out))
print("wrote", dest, "last text y =", y)
