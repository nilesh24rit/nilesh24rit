"""
render_heatmap_svg.py

Draws data/contributions.json as the familiar 53-week x 7-day grid of
rounded boxes. Boxes slide in diagonally on load (CSS keyframes, plays
once), then a legend + stats line sit underneath.

Usage:
    python render_heatmap_svg.py
    -> writes contrib-heatmap.svg
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

LEVEL_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BOX = 11
GAP = 3
LEFT_PAD = 20
TOP_PAD = 20


def load_data() -> dict:
    return json.loads(Path("data/contributions.json").read_text())


def week_columns(days: list[dict]) -> list[list[dict]]:
    """Bucket days into calendar weeks (Sun-Sat) for a 53-column grid."""
    by_date = {d["date"]: d for d in days}
    dates = sorted(by_date.keys())
    if not dates:
        return []

    start = datetime.strptime(dates[0], "%Y-%m-%d")
    start -= timedelta(days=start.weekday() + 1 if start.weekday() != 6 else 0)
    end = datetime.strptime(dates[-1], "%Y-%m-%d")

    weeks, cursor = [], start
    while cursor <= end:
        week = []
        for i in range(7):
            day = cursor + timedelta(days=i)
            key = day.strftime("%Y-%m-%d")
            week.append(by_date.get(key, {"date": key, "level": 0}))
        weeks.append(week)
        cursor += timedelta(days=7)
    return weeks


def build_svg(data: dict) -> str:
    weeks = week_columns(data["days"])
    n_weeks = len(weeks)
    width = LEFT_PAD * 2 + n_weeks * (BOX + GAP)
    grid_height = 7 * (BOX + GAP)
    height = TOP_PAD + grid_height + 70

    style_rules = ["""
        @keyframes cellIn {
          from { opacity: 0; transform: translate(-4px, -4px); }
          to   { opacity: 1; transform: translate(0, 0); }
        }
    """]
    cells_svg = []

    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(week):
            x = LEFT_PAD + w_idx * (BOX + GAP)
            y = TOP_PAD + d_idx * (BOX + GAP)
            color = LEVEL_COLORS[min(day["level"], 4)]
            delay = (w_idx + d_idx) * 0.006
            cells_svg.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2" '
                f'fill="{color}" style="opacity:0; animation: cellIn 0.25s ease-out '
                f'{delay:.3f}s forwards;" />'
            )

    legend_y = TOP_PAD + grid_height + 22
    legend = ['<text x="20" y="' + str(legend_y) + '" font-family="monospace" font-size="11" fill="#8b949e">Less</text>']
    for i, color in enumerate(LEVEL_COLORS):
        lx = 60 + i * (BOX + GAP)
        legend.append(f'<rect x="{lx}" y="{legend_y-9}" width="{BOX}" height="{BOX}" rx="2" fill="{color}"/>')
    legend.append(f'<text x="{60 + 5*(BOX+GAP) + 6}" y="{legend_y}" font-family="monospace" font-size="11" fill="#8b949e">More</text>')

    stats_y = legend_y + 24
    stats_text = (
        f"{data['total_active_days']} active days &#183; "
        f"current streak {data['current_streak']} &#183; "
        f"longest streak {data['longest_streak']}"
    )
    stats = f'<text x="20" y="{stats_y}" font-family="monospace" font-size="12" fill="#c9d1d9">{stats_text}</text>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <style>{''.join(style_rules)}</style>
  <rect x="0" y="0" width="{width}" height="{height}" fill="#0d1117"/>
  {''.join(cells_svg)}
  {''.join(legend)}
  {stats}
</svg>"""


if __name__ == "__main__":
    data = load_data()
    svg = build_svg(data)
    Path("contrib-heatmap.svg").write_text(svg)
    print("Heatmap SVG written -> contrib-heatmap.svg")
