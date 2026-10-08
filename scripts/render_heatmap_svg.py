"""Render data/contributions.json as an animated 53x7 heatmap SVG."""
import json, sys, datetime as dt

SRC = sys.argv[1] if len(sys.argv) > 1 else "data/contributions.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"
# near-black (none) -> blues -> gold; level 5 is a bright gold top end
PALETTE = ["#1a1d24", "#1e3a8a", "#2563eb", "#b8912f", "#d4af37", "#ffd966"]
W = 860
CELL, GAP = 12, 3
PITCH = CELL + GAP
LEFT, TOP = 44, 62
data = json.load(open(SRC))
days = data["days"]

first = dt.date.fromisoformat(days[0]["date"])
first_sun = first - dt.timedelta(days=(first.weekday() + 1) % 7)
counts = sorted(d["count"] for d in days if d["count"] > 0)
top_cut = counts[int(len(counts) * 0.95)] if len(counts) >= 20 else float("inf")

cells, month_labels, last_month = [], [], None
weeks = 0
for d in days:
    date = dt.date.fromisoformat(d["date"])
    wk = (date - first_sun).days // 7
    dow = (date.weekday() + 1) % 7
    weeks = max(weeks, wk + 1)
    lvl = d["level"]
    if lvl >= 4 and d["count"] >= top_cut:
        lvl = 5
    x, y = LEFT + wk * PITCH, TOP + dow * PITCH
    delay = 0.25 + (wk + dow) * 0.012
    tip = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {d["date"]}'
    cells.append(f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" fill="{PALETTE[lvl]}" style="animation-delay:{delay:.2f}s"><title>{tip}</title></rect>')
    if date.day <= 7 and dow == 0 and date.strftime("%b") != last_month:
        month_labels.append(f'<text x="{x}" y="{TOP - 10}" class="l">{date.strftime("%b")}</text>')
        last_month = date.strftime("%b")

grid_w = weeks * PITCH
H = TOP + 7 * PITCH + 52
scale_x = (W - 2 * 18 - LEFT) / max(grid_w, 1)  # normally ~1; keeps edges inside the frame
day_labels = "".join(f'<text x="{LEFT - 10}" y="{TOP + i * PITCH + 10}" text-anchor="end" class="l">{n}</text>'
                     for i, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))

total = data["total"]
if data.get("placeholder"):
    footer = "waiting for the first daily sync from GitHub Actions…"
else:
    footer = (f'{total:,} contributions in the last year  ·  current streak {data["current_streak"]}d'
              f'  ·  longest {data["longest_streak"]}d')

lx = W - 18 - 5 * PITCH - 78
legend = (f'<text x="{lx}" y="{H - 18}" text-anchor="end" class="l">Less</text>'
          + "".join(f'<rect x="{lx + 8 + i * PITCH}" y="{H - 28}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
                    for i, c in enumerate(PALETTE))
          + f'<text x="{lx + 8 + 6 * PITCH + 4}" y="{H - 18}" class="l">More</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="GitHub contribution heatmap">
<style>
.l{{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#8ba3c7}}
.t{{font:13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:#e6edf3}}
.c{{opacity:0;transform-box:fill-box;transform-origin:center;animation:in .5s ease-out both}}
@keyframes in{{from{{opacity:0;transform:translateY(-8px) scale(.6)}}to{{opacity:1;transform:none}}}}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="#050608" stroke="#2a2f3a"/>
<circle cx="22" cy="20" r="5.5" fill="#d4af37"/><circle cx="42" cy="20" r="5.5" fill="#f7dc8a"/><circle cx="62" cy="20" r="5.5" fill="#3b82f6"/>
<text x="{W/2}" y="25" text-anchor="middle" class="l">contributions.sh</text>
<g transform="translate({(W - 2 * 18 - LEFT - grid_w) / 2 + 18 - 0:.1f},0)">
{day_labels}
{"".join(month_labels)}
{"".join(cells)}
</g>
<text x="24" y="{H - 17}" class="t">{footer}</text>
{legend}
</svg>'''
open(OUT, "w", encoding="utf-8").write(svg)
print("wrote", OUT, f"{weeks} weeks, {len(cells)} cells, {W}x{H}")
