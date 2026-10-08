"""Hand-authored neofetch-style info card (animated SVG). STATIC=1 emits a frozen frame."""
import os

STATIC = os.environ.get("STATIC") == "1"
W, H = 700, 650
BG, BORDER, LINE = "#050608", "#2a2f3a", "#1a1d24"
GOLD, GOLD_LT, BLUE, BLUE_LT = "#d4af37", "#f7dc8a", "#3b82f6", "#60a5fa"
VAL, DIM = "#e6edf3", "#8ba3c7"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

USER = "abdalbagitaha-dev"
TAGLINE = "Odoo Functional Consultant · Saudi Arabia"
KEY_X, VAL_X = 44, 196
CH = 9.6    # approx. monospace advance at 16px
CH_S = 8.4  # at 14px
SWATCH = ["#1a1d24", "#1e3a8a", "#2563eb", "#60a5fa", "#8a6d1d", "#b8912f", "#d4af37", "#f7dc8a"]


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def appear(i, base=0.4, step=0.14):
    """fade + slide-in animation tags for the i-th block"""
    if STATIC:
        return ""
    t = base + i * step
    return (f'<animate attributeName="opacity" from="0" to="1" begin="{t:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="-12 0" to="0 0" begin="{t:.2f}s" dur="0.4s" fill="freeze"/>')


def block(i, body):
    op = "1" if STATIC else "0"
    return f'<g opacity="{op}">{appear(i)}{body}</g>'


def key(y, label):
    """gold diamond bullet + label"""
    return (f'<rect x="{KEY_X}" y="{y - 10}" width="8" height="8" fill="{GOLD}" transform="rotate(45 {KEY_X + 4} {y - 6})"/>'
            f'<text x="{KEY_X + 20}" y="{y}" fill="{GOLD}" font-weight="bold">{esc(label)}</text>')


def chips(y, items, stroke, fill, color, gap=8):
    out, x = [], VAL_X
    for it in items:
        w = len(it) * CH_S + 22
        out.append(f'<rect x="{x:.0f}" y="{y - 17}" width="{w:.0f}" height="24" rx="12" fill="{fill}" stroke="{stroke}"/>'
                   f'<text x="{x + w / 2:.0f}" y="{y}" text-anchor="middle" font-size="14" fill="{color}">{esc(it)}</text>')
        x += w + gap
    return "".join(out)


rows = []
y = 196
rows.append(key(y, "Role") + f'<text x="{VAL_X}" y="{y}" fill="{VAL}">Odoo Functional Consultant</text>')
y += 50
rows.append(key(y, "Odoo") + chips(y, ["v18", "v19"], GOLD, "#1c1607", GOLD_LT))
y += 50
rows.append(key(y, "Modules") + chips(y, ["Sales", "Inventory", "POS", "Accounting", "Purchases"], "#1e3a8a", "#0b1426", BLUE_LT, gap=7))
y += 50
rows.append(key(y, "Edu") + f'<text x="{VAL_X}" y="{y}" fill="{VAL}">B.Sc. Information Technology</text>'
            f'<text x="{VAL_X}" y="{y + 22}" fill="{DIM}" font-size="14">Jazan University · 2025</text>')
y += 72
award = "1st Place · Raqeem Accounting Hackathon 2024"
aw = len(award) * CH_S + 46
rows.append(key(y, "Award") +
            f'<rect x="{VAL_X}" y="{y - 18}" width="{aw:.0f}" height="26" rx="6" fill="#1c1607" stroke="{GOLD}" stroke-opacity="0.6"/>'
            f'<text x="{VAL_X + 12}" y="{y}" font-size="14" fill="{GOLD_LT}">★</text>'
            f'<text x="{VAL_X + 32}" y="{y}" font-size="14" fill="{GOLD_LT}">{esc(award)}</text>')
y += 50
rows.append(key(y, "Location") + f'<text x="{VAL_X}" y="{y}" fill="{VAL}">Saudi Arabia</text>')
y += 50
pulse = "" if STATIC else (
    f'<animate attributeName="r" values="5;10;5" dur="2s" repeatCount="indefinite"/>'
    f'<animate attributeName="opacity" values="0.6;0;0.6" dur="2s" repeatCount="indefinite"/>')
rows.append(key(y, "Status") +
            f'<circle cx="{VAL_X + 6}" cy="{y - 5}" r="5" fill="{BLUE_LT}" opacity="0.6">{pulse}</circle>'
            f'<circle cx="{VAL_X + 6}" cy="{y - 5}" r="4" fill="{BLUE_LT}"/>'
            f'<text x="{VAL_X + 20}" y="{y}" fill="{VAL}">Open to roles anywhere in KSA</text>')
last_y = y

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Profile info card">',
       '<defs>'
       f'<linearGradient id="gName" x1="0" x2="1"><stop offset="0" stop-color="{GOLD_LT}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>'
       f'<linearGradient id="gRule" x1="0" x2="1"><stop offset="0" stop-color="{GOLD}"/><stop offset="0.5" stop-color="{BLUE}"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></linearGradient>'
       f'<linearGradient id="gBar" x1="0" x2="1">' + "".join(
           f'<stop offset="{i / (len(SWATCH) - 1):.3f}" stop-color="{c}"/>' for i, c in enumerate(SWATCH)) + '</linearGradient>'
       f'<radialGradient id="gGlow" cx="1" cy="0" r="0.9"><stop offset="0" stop-color="{GOLD}" stop-opacity="0.10"/><stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>'
       f'<radialGradient id="gGlow2" cx="0" cy="1" r="0.8"><stop offset="0" stop-color="{BLUE}" stop-opacity="0.08"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
       '</defs>',
       f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>',
       f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="url(#gGlow)"/>',
       f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="url(#gGlow2)"/>',
       f'<line x1="1" y1="40" x2="{W - 1}" y2="40" stroke="{LINE}"/>',
       f'<circle cx="22" cy="20" r="5.5" fill="{GOLD}"/><circle cx="42" cy="20" r="5.5" fill="{GOLD_LT}"/><circle cx="62" cy="20" r="5.5" fill="{BLUE}"/>',
       f'<text x="{W / 2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{DIM}">neofetch</text>',
       f'<g font-family="{MONO}" font-size="16" xml:space="preserve">']

# header: name, tagline, gradient rule
out.append(block(0, f'<text x="{KEY_X}" y="96" font-size="27" font-weight="bold"><tspan fill="url(#gName)">{USER}</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{BLUE_LT}">github</tspan></text>'))
out.append(block(1, f'<text x="{KEY_X}" y="126" font-size="15" fill="{DIM}">{esc(TAGLINE)}</text>'))
out.append(block(2, f'<rect x="{KEY_X}" y="146" width="{W - 2 * KEY_X}" height="2" rx="1" fill="url(#gRule)"/>'))
for i, r in enumerate(rows):
    out.append(block(3 + i, r))

# palette strip like neofetch's colour blocks
sy = last_y + 56
sw = "".join(f'<rect x="{KEY_X + i * 40}" y="{sy}" width="34" height="18" rx="4" fill="{c}"/>' for i, c in enumerate(SWATCH))
out.append(block(3 + len(rows), sw + f'<rect x="{KEY_X}" y="{sy + 28}" width="{len(SWATCH) * 40 - 6}" height="3" rx="1.5" fill="url(#gBar)"/>'))
out.append('</g></svg>')

dest = "info-card-static.svg" if STATIC else "info-card.svg"
open(dest, "w", encoding="utf-8").write("\n".join(out))
print("wrote", dest, "bottom =", sy + 31, "of", H)
