"""Fetch the public contribution calendar and write data/contributions.json."""
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "muzammil11123"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days(username):
    response = requests.get(
        f"https://github.com/users/{username}/contributions",
        headers={"User-Agent": "profile-art", "X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    counts = {}
    for tip in soup.find_all("tool-tip"):
        match = re.match(r"\s*([\d,]+) contributions? on", tip.get_text())
        counts[tip.get("for")] = int(match.group(1).replace(",", "")) if match else 0

    days = [
        {
            "date": cell["data-date"],
            "level": int(cell.get("data-level", 0)),
            "count": counts.get(cell.get("id"), 0),
        }
        for cell in soup.find_all("td", attrs={"data-date": True})
    ]
    return sorted(days, key=lambda day: day["date"])


def derive_stats(days):
    longest = run = 0
    for day in days:
        run = run + 1 if day["count"] else 0
        longest = max(longest, run)

    # Today does not break a streak until it is over.
    active = {day["date"] for day in days if day["count"]}
    cursor = date.fromisoformat(days[-1]["date"])
    if cursor.isoformat() not in active:
        cursor -= timedelta(days=1)
    current = 0
    while cursor.isoformat() in active:
        current += 1
        cursor -= timedelta(days=1)

    months = defaultdict(int)
    for day in days:
        months[day["date"][:7]] += day["count"]
    best = max(days, key=lambda day: day["count"])

    return {
        "total": sum(day["count"] for day in days),
        "active_days": len(active),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "months": dict(sorted(months.items())),
    }


def main():
    days = fetch_days(USERNAME)
    # A changed page layout must fail the run, not overwrite good data with nothing.
    if len(days) < 300:
        sys.exit(f"Expected about a year of days, got {len(days)}: page layout may have changed.")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(
        json.dumps({"username": USERNAME, "stats": derive_stats(days), "days": days}, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(days)} days to {OUT.name}")


if __name__ == "__main__":
    main()
