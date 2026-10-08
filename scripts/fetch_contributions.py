"""Fetch the public contribution calendar (no token) and write data/contributions.json.
Usage: fetch_contributions.py [username] [--placeholder]"""
import json, re, sys, datetime as dt, os
from collections import OrderedDict

USER = next((a for a in sys.argv[1:] if not a.startswith("--")), os.environ.get("GH_USER", "abdalbagitaha-dev"))
OUT = "data/contributions.json"


def stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"]) if days else {"date": None, "count": 0}
    longest = cur = 0
    for d in days:
        cur = cur + 1 if d["count"] > 0 else 0
        longest = max(longest, cur)
    # current streak: allow today to be empty
    streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            streak += 1
        elif d is days[-1]:
            continue
        else:
            break
    months = OrderedDict()
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
    return {"total": total, "current_streak": streak, "longest_streak": longest,
            "best_day": {"date": best["date"], "count": best["count"]}, "monthly": months}


def placeholder():
    end = dt.date.today()
    start = end - dt.timedelta(days=364)
    start -= dt.timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    days = []
    d = start
    while d <= end:
        days.append({"date": d.isoformat(), "count": 0, "level": 0})
        d += dt.timedelta(days=1)
    return days


def fetch():
    import requests
    from bs4 import BeautifulSoup
    r = requests.get(f"https://github.com/users/{USER}/contributions",
                     headers={"User-Agent": "Mozilla/5.0 (profile-readme-bot)"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    tips = {}
    for t in soup.find_all("tool-tip"):
        m = re.match(r"\s*(No|\d[\d,]*)\s+contribution", t.get_text())
        if m and t.get("for"):
            tips[t["for"]] = 0 if m.group(1) == "No" else int(m.group(1).replace(",", ""))
    days = []
    for c in soup.select("td.ContributionCalendar-day[data-date]"):
        n = tips.get(c.get("id"), 0)
        days.append({"date": c["data-date"], "count": n, "level": int(c.get("data-level", 0))})
    if not days:
        raise RuntimeError("no contribution cells found - page layout changed?")
    days.sort(key=lambda d: d["date"])
    return days


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    is_placeholder = "--placeholder" in sys.argv
    days = placeholder() if is_placeholder else fetch()
    data = {"user": USER, "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "placeholder": is_placeholder, "days": days, **stats(days)}
    json.dump(data, open(OUT, "w"), indent=1)
    print(f"wrote {OUT}: {len(days)} days, {data['total']} contributions (placeholder={is_placeholder})")
