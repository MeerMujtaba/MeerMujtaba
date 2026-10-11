#!/usr/bin/env python3
"""Hand-authored neofetch-style info card SVG with staggered line animation."""
import os
from xml.sax.saxutils import escape

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "info-card.svg")

W = 490
GREEN = "#39d353"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
TITLE_H, LINE_H, PAD = 38, 30, 22

ROWS = [
    ("prompt", None, "$ whoami"),
    ("kv", "name", "Meer Mujtaba Khan"),
    ("kv", "role", "CSE Student @ MUET"),
    ("kv", "stack", "Java · C++ · JS/TS · HTML/CSS"),
    ("kv", "focus", "Swing apps · DSA · frontend"),
    ("kv", "ships", "HESCO billing · 3D chess site"),
    ("kv", "ieee", "Tech Coordinator, IEEE IMS"),
    ("kv", "mail", "meermujtaba@gmail.com"),
]


def main():
    body_h = len(ROWS) * LINE_H + 28
    H = TITLE_H + body_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="About Meer Mujtaba">',
        "<style>",
        "text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}",
        ".line{opacity:0;animation:fadeSlide .5s ease-out forwards;}",
        "@keyframes fadeSlide{from{opacity:0;transform:translateX(-10px);}to{opacity:1;transform:translateX(0);}}",
        ".cursor{animation:blink 1.1s steps(1) infinite;}",
        "@keyframes blink{50%{opacity:0;}}",
        "</style>",
        f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
        # title bar
        f'<rect width="{W}" height="{TITLE_H}" rx="10" fill="#161b22"/>',
        f'<rect y="{TITLE_H - 10}" width="{W}" height="10" fill="#161b22"/>',
        f'<circle cx="24" cy="{TITLE_H // 2}" r="6" fill="#ff5f57"/>',
        f'<circle cx="44" cy="{TITLE_H // 2}" r="6" fill="#febc2e"/>',
        f'<circle cx="64" cy="{TITLE_H // 2}" r="6" fill="#28c840"/>',
        f'<text x="{W // 2}" y="{TITLE_H // 2 + 5}" font-size="13" fill="{MUTED}" text-anchor="middle">meer@github: ~</text>',
    ]

    y = TITLE_H + PAD + 12
    for i, (kind, key, val) in enumerate(ROWS):
        delay = 0.3 + i * 0.22
        parts.append(f'<g class="line" style="animation-delay:{delay:.2f}s">')
        if kind == "prompt":
            parts.append(
                f'<text x="{PAD}" y="{y}" font-size="14" fill="{GREEN}" font-weight="bold">'
                f'meer@github:~$ <tspan fill="{TEXT}">{escape(val)}</tspan></text>'
            )
        else:
            parts.append(
                f'<text x="{PAD}" y="{y}" font-size="14">'
                f'<tspan fill="{GREEN}">{escape(key)}</tspan>'
                f'<tspan fill="{MUTED}"> {"·" * 1} </tspan>'
                f'<tspan fill="{TEXT}">{escape(val)}</tspan></text>'
            )
        parts.append("</g>")
        y += LINE_H

    # blinking cursor on the last line
    total = 0.3 + len(ROWS) * 0.22
    parts.append(
        f'<rect class="cursor" x="{W - PAD - 12}" y="{y - LINE_H + 2}" width="10" height="16" fill="{GREEN}" '
        f'style="animation-delay:{total:.2f}s"/>'
    )
    parts.append("</svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
