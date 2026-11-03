"""Write the animated ASCII portrait: ascii-portrait.svg.

Uses source-prepped.png (from prep_photo.py) when it exists; otherwise draws an
arc reactor. Each row is wiped left to right by a block cursor, staggered top to
bottom. The animation plays once and freezes.
"""
import math
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
PHOTO = ROOT / "source-prepped.png"
WIDTH, HEIGHT = 370, 340
BAR_HEIGHT = 30
COLUMNS, ROWS = 76, 37
CHAR_WIDTH, LINE_HEIGHT, FONT_SIZE = 4.5, 8, 7.5
RAMP = " .:-=+*#%@"  # The leading space leaves the background clear.
BG, BAR, BORDER, MUTED, CYAN = "#0b1118", "#121b25", "#223040", "#7d8fa3", "#5fe3ff"
FILL = "#b9c7d4"


def arc_reactor(width, height):
    """Draw a reactor as a brightness map where 1 is the densest glyph."""
    size = 1200
    canvas = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(canvas)
    center = size / 2

    def box(radius):
        return (center - radius, center - radius, center + radius, center + radius)

    draw.ellipse(box(570), outline=235, width=34)
    draw.ellipse(box(490), outline=120, width=16)
    for index in range(10):
        start = index * 36 + 4
        for radius, level in ((440, 215), (395, 150), (350, 215)):
            draw.arc(box(radius), start, start + 26, fill=level, width=30)
    draw.ellipse(box(290), outline=170, width=20)
    triangle = [
        (center + 255 * math.cos(math.radians(a)), center + 255 * math.sin(math.radians(a)))
        for a in (-90, 30, 150)
    ]
    draw.polygon(triangle, outline=250, width=24)
    glow = Image.new("L", (size, size), 0)
    ImageDraw.Draw(glow).ellipse(box(120), fill=255)
    canvas = Image.fromarray(
        np.maximum(np.asarray(canvas), np.asarray(glow.filter(ImageFilter.GaussianBlur(45))))
    )

    # Fit the circle inside the character grid, correcting for tall glyph cells.
    field = Image.new("L", (width, height), 0)
    circle_rows = height - 2
    circle_columns = round(circle_rows * LINE_HEIGHT / CHAR_WIDTH)
    resized = canvas.resize((circle_columns, circle_rows), Image.LANCZOS)
    field.paste(resized, ((width - circle_columns) // 2, 1))
    return np.asarray(field, dtype=np.float32) / 255


def photo_density(width, height):
    """Dark pixels become dense glyphs, so the white background stays empty."""
    image = Image.open(PHOTO).convert("L")
    target = (width * CHAR_WIDTH) / (height * LINE_HEIGHT)
    w, h = image.size
    if w / h > target:
        crop = round(h * target)
        image = image.crop(((w - crop) // 2, 0, (w + crop) // 2, h))
    else:
        crop = round(w / target)
        image = image.crop((0, 0, w, crop))  # Keep the top, where the face is.
    return 1 - np.asarray(image.resize((width, height), Image.LANCZOS), dtype=np.float32) / 255


def main():
    density = photo_density(COLUMNS, ROWS) if PHOTO.exists() else arc_reactor(COLUMNS, ROWS)
    indexes = np.clip((density * len(RAMP)).astype(int), 0, len(RAMP) - 1)
    text_width = COLUMNS * CHAR_WIDTH
    left = (WIDTH - text_width) / 2
    top = BAR_HEIGHT + (HEIGHT - BAR_HEIGHT - ROWS * LINE_HEIGHT) / 2

    rows = []
    for row in range(ROWS):
        line = "".join(RAMP[i] for i in indexes[row])
        y = top + row * LINE_HEIGHT
        rows.append(
            f'<text x="{left}" y="{y + 6.5}" textLength="{text_width}" lengthAdjust="spacing" '
            f'xml:space="preserve">{escape(line)}</text>'
            f'<g class="w" style="animation-delay:{row * 0.055:.3f}s">'
            f'<rect x="{left}" y="{y}" width="{text_width + 6}" height="{LINE_HEIGHT}" fill="{BG}"/>'
            f'<rect x="{left}" y="{y}" width="5" height="{LINE_HEIGHT}" fill="{CYAN}"/></g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="ASCII art portrait">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Consolas,Menlo,monospace}}
.a text{{font-size:{FONT_SIZE}px;fill:{FILL};white-space:pre}}
.t{{font-size:12px;fill:{MUTED}}}
.w{{animation:wipe .75s linear forwards}}
@keyframes wipe{{from{{transform:translateX(0)}}to{{transform:translateX({text_width + 12}px)}}}}
@media (prefers-reduced-motion:reduce){{.w{{display:none}}}}
</style>
<defs><clipPath id="v"><rect x="{left - 1}" y="{BAR_HEIGHT}" width="{text_width + 2}" height="{HEIGHT - BAR_HEIGHT - 1}"/></clipPath></defs>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M1 30V11a10 10 0 0 1 10-10h{WIDTH - 22}a10 10 0 0 1 10 10v19z" fill="{BAR}"/>
<circle cx="18" cy="15.500" r="5" fill="#ff5f56"/><circle cx="36" cy="15.500" r="5" fill="#ffbd2e"/><circle cx="54" cy="15.500" r="5" fill="#27c93f"/>
<text x="{WIDTH / 2}" y="20" text-anchor="middle" class="t">whoami</text>
<g class="a" clip-path="url(#v)">
{chr(10).join(rows)}
</g>
</svg>
'''
    (ROOT / "ascii-portrait.svg").write_text(svg, encoding="utf-8")
    source = PHOTO.name if PHOTO.exists() else "arc reactor"
    print(f"Wrote ascii-portrait.svg from {source} ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
