"""
make_ascii_svg.py

Converts prepped-source.png into an ASCII-art SVG that "types" itself in
row by row using SMIL animation (plays once, then freezes - GitHub renders
SMIL fine inside <img>-embedded SVGs, but strips <script> tags).

Usage:
    python make_ascii_svg.py
    -> writes nilesh-ascii.svg
"""

from PIL import Image

GLYPHS = " .`:-=+*cs#%@"   # sparse (bright) -> dense (dark); leading space -> blank
COLS, ROWS = 100, 53
CELL_W, CELL_H = 7, 12
FILL_COLOR = "#8b949e"     # single monochrome tone - no per-char rainbow


def image_to_ascii_rows(path: str) -> list[str]:
    img = Image.open(path).convert("L").resize((COLS, ROWS))
    pixels = img.load()
    rows = []
    for y in range(ROWS):
        line = []
        for x in range(COLS):
            brightness = pixels[x, y] / 255.0
            idx = int((1 - brightness) * (len(GLYPHS) - 1))
            line.append(GLYPHS[idx])
        rows.append("".join(line))
    return rows


def build_svg(rows: list[str]) -> str:
    width = COLS * CELL_W
    height = ROWS * CELL_H
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="monospace" font-size="{CELL_H}">'
    ]

    for row_idx, row_text in enumerate(rows):
        y = (row_idx + 1) * CELL_H
        delay = row_idx * 0.045  # stagger: top row first, cascading down
        clip_id = f"wipe{row_idx}"
        text_escaped = (
            row_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        )

        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(f'  <rect x="0" y="{y - CELL_H}" width="0" height="{CELL_H}">')
        parts.append(
            f'    <animate attributeName="width" from="0" to="{width}" '
            f'begin="{delay:.3f}s" dur="0.35s" fill="freeze" />'
        )
        parts.append("  </rect>")
        parts.append("</clipPath>")

        parts.append(f'<g clip-path="url(#{clip_id})">')
        parts.append(
            f'  <text x="0" y="{y}" fill="{FILL_COLOR}" xml:space="preserve">{text_escaped}</text>'
        )
        parts.append("</g>")

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    rows = image_to_ascii_rows("prepped-source.png")
    svg = build_svg(rows)
    with open("nilesh-ascii.svg", "w") as f:
        f.write(svg)
    print("ASCII portrait SVG written -> nilesh-ascii.svg")
