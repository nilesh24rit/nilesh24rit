"""
fetch_contributions.py

GitHub serves each user's contribution calendar as a public HTML fragment
at /users/<username>/contributions - the same markup the profile page
itself uses. No GraphQL API, no personal access token required.

Usage:
    python fetch_contributions.py YOUR_USERNAME
    -> writes data/contributions.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

CALENDAR_URL = "https://github.com/users/{username}/contributions"


def fetch(username: str) -> dict:
    resp = requests.get(
        CALENDAR_URL.format(username=username),
        headers={"User-Agent": "profile-art-bot"},
        timeout=15,
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    days = []
    for cell in soup.select("td.ContributionCalendar-day, [data-date]"):
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None:
            continue
        days.append({"date": date, "level": int(level) if level is not None else 0})

    days.sort(key=lambda d: d["date"])

    total = sum(1 for d in days if d["level"] > 0)

    # "Today" (UTC) may legitimately still show level 0 simply because the
    # day isn't over yet / GitHub's calendar hasn't refreshed since the
    # latest commit. That shouldn't zero out an otherwise-live streak, so
    # skip today's cell (once) if it's the very last entry and has no
    # contributions yet, then keep counting backwards as normal.
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    current_streak = 0
    for i, d in enumerate(reversed(days)):
        if d["level"] > 0:
            current_streak += 1
        elif i == 0 and d["date"] == today_str:
            continue  # today, not over yet - don't break the streak
        else:
            break

    longest_streak, running = 0, 0
    for d in days:
        if d["level"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    return {
        "username": username,
        "days": days,
        "total_active_days": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetch_contributions.py <github_username>")
        sys.exit(1)

    data = fetch(sys.argv[1])
    Path("data").mkdir(exist_ok=True)
    Path("data/contributions.json").write_text(json.dumps(data, indent=2))
    print(f"wrote data/contributions.json ({data['total_active_days']} active days)")