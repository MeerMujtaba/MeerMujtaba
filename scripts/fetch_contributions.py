#!/usr/bin/env python3
"""Fetch the public contribution calendar (no token needed) and write
data/contributions.json with per-day counts plus derived stats."""
import datetime
import json
import os
import re
import sys
import urllib.request

USER = "MeerMujtaba"
URL = f"https://github.com/users/{USER}/contributions"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "data", "contributions.json")


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            html = f.read()
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

    cells = {}  # component id -> {date, level, count}
    for m in re.finditer(
        r'data-date="(\d{4}-\d{2}-\d{2})" id="(contribution-day-component-[\d-]+)" data-level="(\d)"',
        html,
    ):
        date, comp_id, level = m.groups()
        cells[comp_id] = {"date": date, "level": int(level), "count": 0}

    for m in re.finditer(
        r'for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)</tool-tip>', html
    ):
        comp_id, tip = m.groups()
        if comp_id not in cells:
            continue
        if tip.startswith("No contributions"):
            cells[comp_id]["count"] = 0
        else:
            cm = re.match(r"([\d,]+) contribution", tip)
            cells[comp_id]["count"] = (
                int(cm.group(1).replace(",", "")) if cm else 0
            )

    days = sorted(cells.values(), key=lambda d: d["date"])
    if not days:
        raise SystemExit("no contribution cells parsed")

    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])

    # current streak: walk back from the most recent active day
    counts = [d["count"] for d in days]
    i = len(counts) - 1
    if counts[i] == 0:
        i -= 1  # today may not be over yet
    current_streak = 0
    while i >= 0 and counts[i] > 0:
        current_streak += 1
        i -= 1

    longest, run = 0, 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = {
        "user": USER,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "days": days,
        "stats": {
            "total": total,
            "current_streak": current_streak,
            "longest_streak": longest,
            "best_day": {"date": best["date"], "count": best["count"]},
            "range": {"from": days[0]["date"], "to": days[-1]["date"]},
        },
    }
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"wrote {OUT}: {len(days)} days, {total} contributions, "
          f"streak {current_streak}, longest {longest}")


if __name__ == "__main__":
    main()
