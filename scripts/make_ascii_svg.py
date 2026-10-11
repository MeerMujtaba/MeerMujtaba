#!/usr/bin/env python3
"""Convert the profile photo to a self-typing green ASCII-art SVG."""
import os
from xml.sax.saxutils import escape

from PIL import Image, ImageEnhance, ImageOps

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "profile.jpg")
OUT = os.path.join(BASE, "meer-ascii.svg")

COLS = 88
RAMP = " .`:-=+*#%@"  # sparse -> dense
GREEN = "#39d353"
CHAR_W, ROW_H, FONT_SIZE = 7.0, 13, 12
PAD = 16
ROW_DELAY, ROW_DUR = 0.07, 0.45


def main():
    im = Image.open(SRC).convert("RGB")
    # focus on head + shoulders
    im = im.crop((120, 30, 720, 800))
    g = ImageOps.grayscale(im)
    g = ImageOps.autocontrast(g, cutoff=2)
    g = ImageEnhance.Contrast(g).enhance(1.5)
    g = ImageOps.invert(g)  # dark features -> dense green
    # wash the near-black studio background out to spaces
    g = g.point(lambda v: 0 if v > 220 else v)
    rows_n = round(COLS * (g.height / g.width) / 2.0)
    g = g.resize((COLS, rows_n), Image.LANCZOS)
    px = g.load()

    row_w = COLS * CHAR_W
    W = int(row_w + PAD * 2)
    H = int(rows_n * ROW_H + PAD * 2)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ASCII portrait of Meer Mujtaba">',
        f'<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>',
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FONT_SIZE}" fill="{GREEN}">',
    ]
    for r in range(rows_n):
        chars = []
        for c in range(COLS):
            v = px[c, r]
            chars.append(RAMP[min(v * len(RAMP) // 256, len(RAMP) - 1)])
        line = escape("".join(chars))
        y = PAD + r * ROW_H + FONT_SIZE
        begin = r * ROW_DELAY
        parts.append(f'<clipPath id="clip{r}"><rect x="{PAD}" y="{PAD + r * ROW_H}" width="0" height="{ROW_H}">'
                     f'<animate attributeName="width" from="0" to="{row_w}" dur="{ROW_DUR}s" '
                     f'begin="{begin:.2f}s" fill="freeze"/></rect></clipPath>')
        parts.append(f'<g clip-path="url(#clip{r})"><text x="{PAD}" y="{y}" textLength="{row_w}" '
                     f'lengthAdjust="spacing" xml:space="preserve">{line}</text></g>')

    # blinking block cursor after the portrait finishes typing
    total = rows_n * ROW_DELAY + ROW_DUR
    cy = PAD + (rows_n - 1) * ROW_H + 2
    parts.append(
        f'<rect x="{PAD + row_w + 4}" y="{cy}" width="9" height="{FONT_SIZE}" fill="{GREEN}">'
        f'<animate attributeName="opacity" values="1;0;1" dur="1s" begin="{total:.2f}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="0" dur="0.01s" begin="0s" fill="freeze"/></rect>'
    )
    parts.append("</g></svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {OUT} ({W}x{H}, {rows_n} rows)")


if __name__ == "__main__":
    main()
