"""Render data/contributions.json as an animated heatmap: contrib-heatmap.svg."""
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PALETTE = ["#16212c", "#0e4a5c", "#117a92", "#25b4cf", "#5fe3ff"]
BG, BORDER, MUTED, GOLD = "#0b1118", "#223040", "#7d8fa3", "#ffc857"
CELL, PITCH = 12, 15
LEFT, TOP = 42, 38


def short_date(iso):
    when = date.fromisoformat(iso)
    return f"{when:%b} {when.day}"


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text(encoding="utf-8"))
    days, stats = data["days"], data["stats"]
    start = date.fromisoformat(days[0]["date"])
    origin = start.toordinal() - (start.weekday() + 1) % 7  # Sunday of the first week

    cells, month_labels = [], []
    last_month, last_label_col, columns, diagonals = None, -9, 0, 0
    for day in days:
        when = date.fromisoformat(day["date"])
        col = (when.toordinal() - origin) // 7
        row = (when.weekday() + 1) % 7
        columns = max(columns, col + 1)
        diagonals = max(diagonals, col + row)
        cells.append(
            f'<rect class="c d{col + row}" x="{LEFT + col * PITCH}" y="{TOP + row * PITCH}" '
            f'width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[day["level"]]}"/>'
        )
        # Label a month at its first full week, unless it would collide with the last label.
        if row == 0 and when.month != last_month and col - last_label_col >= 3:
            month_labels.append(f'<text x="{LEFT + col * PITCH}" y="{TOP - 9}" class="m">{when:%b}</text>')
            last_month, last_label_col = when.month, col

    width = LEFT + columns * PITCH + 15
    grid_bottom = TOP + 7 * PITCH
    height = grid_bottom + 42
    footer_y = grid_bottom + 24

    weekdays = "".join(
        f'<text x="{LEFT - 8}" y="{TOP + row * PITCH + 10}" class="m" text-anchor="end">{label}</text>'
        for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    legend_x = width - 15 - (30 + 5 * PITCH + 30)
    legend = f'<text x="{legend_x}" y="{footer_y}" class="m">Less</text>'
    for index, color in enumerate(PALETTE):
        legend += (
            f'<rect x="{legend_x + 30 + index * PITCH}" y="{footer_y - 10}" width="{CELL}" '
            f'height="{CELL}" rx="2.5" fill="{color}"/>'
        )
    legend += f'<text x="{legend_x + 30 + 5 * PITCH + 3}" y="{footer_y}" class="m">More</text>'

    parts = [
        ("contributions", stats["total"]),
        ("active days", stats["active_days"]),
        ("current streak", stats["current_streak"]),
        ("longest streak", stats["longest_streak"]),
    ]
    summary = '<tspan class="sep"> / </tspan>'.join(
        f'<tspan class="n">{value}</tspan> {label}' for label, value in parts
    )

    delays = "".join(f".d{i}{{animation-delay:{i * 0.018:.3f}s}}" for i in range(diagonals + 1))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Contribution heatmap: {stats["total"]} contributions in the last year">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Consolas,Menlo,monospace}}
.m{{font-size:10.5px;fill:{MUTED}}}
.s{{font-size:11.5px;fill:{MUTED}}}
.n{{fill:{GOLD};font-weight:700}}
.sep{{fill:{BORDER}}}
.c{{opacity:0;animation:in .45s ease-out forwards}}
@keyframes in{{from{{opacity:0;transform:translate(-8px,-8px)}}to{{opacity:1;transform:none}}}}
{delays}
@media (prefers-reduced-motion:reduce){{.c{{animation:none;opacity:1}}}}
</style>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
{"".join(month_labels)}{weekdays}
{"".join(cells)}
<text x="{LEFT}" y="{footer_y}" class="s">{summary}</text>
{legend}
</svg>
'''
    (ROOT / "contrib-heatmap.svg").write_text(svg, encoding="utf-8")
    print(f"Wrote contrib-heatmap.svg ({len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
