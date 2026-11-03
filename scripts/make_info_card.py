"""Write the neofetch-style card: info-card.svg. STATIC=1 freezes it for previews."""
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 490, 340
BG, BAR, BORDER, MUTED, TEXT, CYAN, GOLD = (
    "#0b1118", "#121b25", "#223040", "#7d8fa3", "#d7e3ee", "#5fe3ff", "#ffc857",
)

# Edit these rows to update the card.
ROWS = [
    ("Role", ["Engineer by degree. Inventor by instinct."]),
    ("Building", ["J.A.R.V.I.S. Mark 3", "voice assistant with a holographic UI"]),
    ("Shipped", ["AI video analyzer for Mantrahackathon", "YOLOv8 · BLIP-2 · Coqui STT · Ollama"]),
    ("Stack", ["TypeScript · React · Three.js · GLSL", "Python · Kotlin · Node.js"]),
    ("Motto", ["Building the future, one commit at a time."]),
    ("Status", ["Sometimes I am the upgrade."]),
]
SWATCHES = ["#ff5f56", "#ffbd2e", "#ffc857", "#27c93f", "#25b4cf", "#5fe3ff", "#b48ead", "#d7e3ee"]


def main():
    static = os.environ.get("STATIC") == "1"
    lines, y, step = [], 62, 22
    delay = 0.1

    def add(markup):
        nonlocal delay
        lines.append(f'<g class="l" style="animation-delay:{delay:.2f}s">{markup}</g>')
        delay += 0.11

    add(f'<text x="24" y="{y}" class="h">muzammil<tspan class="k">@</tspan>github</text>')
    y += 12
    add(f'<rect x="24" y="{y}" width="442" height="1" fill="{BORDER}"/>')
    y += 22
    for key, values in ROWS:
        for index, value in enumerate(values):
            label = f'<text x="24" y="{y}" class="k">{key}</text>' if index == 0 else ""
            tone = "v" if index == 0 else "d"
            add(f'{label}<text x="106" y="{y}" class="{tone}">{escape(value)}</text>')
            y += step
    y -= 6
    add("".join(
        f'<rect x="{24 + index * 24}" y="{y}" width="20" height="10" rx="2" fill="{color}"/>'
        for index, color in enumerate(SWATCHES)
    ))

    animation = "" if static else f"""
.l{{opacity:0;animation:in .5s ease-out forwards}}
.cur{{animation:blink 1.1s steps(2,jump-none) infinite}}
@keyframes in{{from{{opacity:0;transform:translateX(-10px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{from{{opacity:1}}to{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.l{{animation:none;opacity:1}}.cur{{animation:none}}}}"""

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Muzammil: engineer and inventor building J.A.R.V.I.S. Mark 3">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Consolas,Menlo,monospace;font-size:13px}}
.t{{fill:{MUTED};font-size:12px}}
.h{{fill:{GOLD};font-weight:700;font-size:14px}}
.k{{fill:{CYAN}}}
.v{{fill:{TEXT}}}
.d{{fill:{MUTED}}}{animation}
</style>
<rect x=".5" y=".5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M1 30V11a10 10 0 0 1 10-10h{WIDTH - 22}a10 10 0 0 1 10 10v19z" fill="{BAR}"/>
<circle cx="18" cy="15.500" r="5" fill="#ff5f56"/><circle cx="36" cy="15.500" r="5" fill="#ffbd2e"/><circle cx="54" cy="15.500" r="5" fill="#27c93f"/>
<text x="{WIDTH / 2}" y="20" text-anchor="middle" class="t">neofetch</text>
{chr(10).join(lines)}
<rect class="cur" x="{24 + len(SWATCHES) * 24}" y="{y}" width="7" height="10" fill="{CYAN}"/>
</svg>
'''
    (ROOT / "info-card.svg").write_text(svg, encoding="utf-8")
    print("Wrote info-card.svg")


if __name__ == "__main__":
    main()
