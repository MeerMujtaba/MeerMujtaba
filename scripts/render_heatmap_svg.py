#!/usr/bin/env python3
"""Render data/contributions.json as an animated contribution heatmap SVG."""
import datetime
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = os.path.join(BASE, "data", "contributions.json")
OUT = os.path.join(BASE, "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
GREEN = "#39d353"
MUTED = "#8b949e"
TEXT = "#c9d1d9"

CELL, PITCH = 12, 16
PAD_X, PAD_TOP, PAD_BOTTOM = 24, 20, 16
LEGEND_H, FOOTER_H = 30, 26


def main():
    with open(IN) as f:
        data = json.load(f)
    days = data["days"]
    stats = data["stats"]

    first = datetime.date.fromisoformat(days[0]["date"])
    # columns start on the Sunday on/before the first date
    start_sunday = first - datetime.timedelta(days=(first.weekday() + 1) % 7)

    cells = []
    for d in days:
        dt = datetime.date.fromisoformat(d["date"])
        delta = (dt - start_sunday).days
        col, row = divmod(delta, 7)
        cells.append((col, row, d["level"], d["date"], d["count"]))

    ncols = max(c[0] for c in cells) + 1
    grid_w = (ncols - 1) * PITCH + CELL
    grid_h = 6 * PITCH + CELL
    W = PAD_X * 2 + grid_w
    H = PAD_TOP + grid_h + LEGEND_H + FOOTER_H + PAD_BOTTOM
    legend_y = PAD_TOP + grid_h + 14
    footer_y = legend_y + LEGEND_H + 4

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contribution heatmap">',
        "<style>",
        ".cell{transform-box:fill-box;transform-origin:center;opacity:0;"
        "animation:rise .45s cubic-bezier(.2,.7,.3,1.2) both;}",
        "@keyframes rise{from{opacity:0;transform:translateY(10px) scale(.4);}"
        "to{opacity:1;transform:translateY(0) scale(1);}}",
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}",
        "</style>",
        f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
    ]
    for col, row, level, date, count in cells:
        x = PAD_X + col * PITCH
        y = PAD_TOP + row * PITCH
        delay = (col + row) * 30
        title = f"{count} contribution{'s' if count != 1 else ''} on {date}"
        parts.append(
            f'<rect class="cell" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3"'
            f' fill="{PALETTE[level]}" style="animation-delay:{delay}ms"><title>{title}</title></rect>'
        )

    # legend
    lx = W - PAD_X - 5 * (CELL + 4) - 92
    parts.append(f'<text x="{lx}" y="{legend_y + 10}" font-size="12" fill="{MUTED}">Less</text>')
    for i, c in enumerate(PALETTE):
        parts.append(
            f'<rect x="{lx + 44 + i * (CELL + 4)}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="3" fill="{c}"/>'
        )
    parts.append(f'<text x="{lx + 44 + 5 * (CELL + 4) + 8}" y="{legend_y + 10}" font-size="12" fill="{MUTED}">More</text>')

    # footer stats
    total = stats["total"]
    parts.append(
        f'<text x="{PAD_X}" y="{footer_y}" font-size="13" fill="{TEXT}">'
        f'<tspan fill="{GREEN}" font-weight="bold">{total}</tspan> contributions in the last year</text>'
    )
    parts.append(
        f'<text x="{W - PAD_X}" y="{footer_y}" font-size="13" fill="{MUTED}" text-anchor="end">'
        f'streak <tspan fill="{GREEN}" font-weight="bold">{stats["current_streak"]}d</tspan>'
        f' · longest <tspan fill="{TEXT}">{stats["longest_streak"]}d</tspan></text>'
    )
    parts.append("</svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
