#!/usr/bin/env python3
"""
Monthly CRM merge for Nine Agency.
Reads all crm/week-{YYYY}-W{NN}.md files for the target month,
merges every lead row, deduplicates by business name (keeping the
most advanced pipeline stage), and writes crm/monthly-{YYYY-MM}.md
with a full report: pipeline funnel, city performance, niche breakdown,
revenue forecast, and a plain-text executive summary.
"""

import datetime
import glob
import os
import re
import sys

STAGES = [
    "Found", "Emailed", "DM'd", "Replied",
    "Warm", "Call Booked", "Proposal Sent", "Won", "Lost"
]
STAGE_RANK = {s: i for i, s in enumerate(STAGES)}

TIER_MIDPOINTS = {
    "Full Rebuild":   13000,
    "Growth Package":  6000,
    "Upgrade Package": 3000,
    "Quick-Win Package": 1400,
    "Maintenance/SEO":   550,
}


def iso_week_in_month(filepath: str, year: int, month: int) -> bool:
    m = re.search(r"week-(\d{4})-W(\d{2})\.md", filepath)
    if not m:
        return False
    y, w = int(m.group(1)), int(m.group(2))
    if y != year:
        return False
    # check if any day of this ISO week falls in the target month
    monday = datetime.date.fromisocalendar(y, w, 1)
    for d in range(7):
        day = monday + datetime.timedelta(days=d)
        if day.year == year and day.month == month:
            return True
    return False


def parse_week_file(filepath: str) -> list[dict]:
    leads = []
    with open(filepath) as f:
        content = f.read()

    # extract rows from the Lead Tracker table
    rows = re.findall(
        r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*"
        r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]*?)\s*\|",
        content
    )
    for row in rows:
        business, city, niche, contact, stage, last_action, next_action, value, notes = row
        if business.lower() in ("business", "---", ""):
            continue
        stage = stage.strip()
        if stage not in STAGE_RANK:
            continue
        leads.append({
            "business": business.strip(),
            "city":     city.strip(),
            "niche":    niche.strip(),
            "contact":  contact.strip(),
            "stage":    stage,
            "last_action": last_action.strip(),
            "next_action": next_action.strip(),
            "value":    value.strip(),
            "notes":    notes.strip(),
            "source":   os.path.basename(filepath),
        })
    return leads


def deduplicate(leads: list[dict]) -> list[dict]:
    """Keep most advanced stage per business name."""
    best: dict[str, dict] = {}
    for lead in leads:
        key = lead["business"].lower()
        if key not in best:
            best[key] = lead
        else:
            if STAGE_RANK.get(lead["stage"], 0) > STAGE_RANK.get(best[key]["stage"], 0):
                best[key] = lead
    return list(best.values())


def estimate_value(value_str: str) -> int:
    for tier, midpoint in TIER_MIDPOINTS.items():
        if tier.lower() in value_str.lower():
            return midpoint
    # try parsing a number directly
    nums = re.findall(r"\d[\d,]*", value_str.replace(",", ""))
    if nums:
        return int(nums[0])
    return 0


def build_report(leads: list[dict], year: int, month: int) -> str:
    month_name = datetime.date(year, month, 1).strftime("%B %Y")
    lines = [
        f"# Nine Agency — Monthly CRM Report: {month_name}",
        f"**Generated:** {datetime.date.today().isoformat()}  ",
        f"**Total leads tracked:** {len(leads)}  ",
        "",
        "---",
        "",
    ]

    # ── Pipeline funnel ──────────────────────────────────────────────────────
    stage_counts = {s: 0 for s in STAGES}
    stage_value: dict[str, int] = {s: 0 for s in STAGES}
    for lead in leads:
        s = lead["stage"]
        stage_counts[s] = stage_counts.get(s, 0) + 1
        v = estimate_value(lead["value"])
        stage_value[s] = stage_value.get(s, 0) + v

    lines += ["## Pipeline Funnel", ""]
    lines += ["| Stage | Leads | Est. Value | Conversion |", "|---|---|---|---|"]
    prev = len(leads) or 1
    for stage in STAGES:
        count = stage_counts[stage]
        val = f"${stage_value[stage]:,}" if stage_value[stage] else "—"
        conv = f"{count/prev*100:.0f}%" if prev else "—"
        lines.append(f"| {stage} | {count} | {val} | {conv} |")
        if count:
            prev = count
    lines.append("")

    # ── Revenue forecast ─────────────────────────────────────────────────────
    warm_plus = [l for l in leads if STAGE_RANK.get(l["stage"], 0) >= STAGE_RANK["Warm"]]
    forecast_low  = sum(estimate_value(l["value"]) * 0.3 for l in warm_plus)
    forecast_high = sum(estimate_value(l["value"]) * 0.7 for l in warm_plus)
    won_value = sum(estimate_value(l["value"]) for l in leads if l["stage"] == "Won")

    lines += [
        "## Revenue",
        "",
        f"**Closed (Won):** ${won_value:,}  ",
        f"**Pipeline forecast (warm+):** ${forecast_low:,.0f} – ${forecast_high:,.0f}  ",
        "",
    ]

    # ── Niche breakdown ──────────────────────────────────────────────────────
    niches: dict[str, dict] = {}
    for lead in leads:
        n = lead["niche"] or "unknown"
        if n not in niches:
            niches[n] = {"total": 0, "warm": 0, "won": 0}
        niches[n]["total"] += 1
        if STAGE_RANK.get(lead["stage"], 0) >= STAGE_RANK["Warm"]:
            niches[n]["warm"] += 1
        if lead["stage"] == "Won":
            niches[n]["won"] += 1

    lines += ["## Niche Performance", ""]
    lines += ["| Niche | Total | Warm+ | Won | Warm Rate |", "|---|---|---|---|---|"]
    for n, d in sorted(niches.items(), key=lambda x: x[1]["warm"], reverse=True):
        rate = f"{d['warm']/d['total']*100:.0f}%" if d["total"] else "—"
        lines.append(f"| {n} | {d['total']} | {d['warm']} | {d['won']} | {rate} |")
    lines.append("")

    # ── City breakdown ───────────────────────────────────────────────────────
    cities: dict[str, dict] = {}
    for lead in leads:
        c = lead["city"].split(",")[0].strip() or "unknown"
        if c not in cities:
            cities[c] = {"total": 0, "warm": 0}
        cities[c]["total"] += 1
        if STAGE_RANK.get(lead["stage"], 0) >= STAGE_RANK["Warm"]:
            cities[c]["warm"] += 1

    top_cities = sorted(cities.items(), key=lambda x: x[1]["warm"], reverse=True)[:10]
    lines += ["## Top Cities (by warm leads)", ""]
    lines += ["| City | Total Leads | Warm+ |", "|---|---|---|"]
    for c, d in top_cities:
        lines.append(f"| {c} | {d['total']} | {d['warm']} |")
    lines.append("")

    # ── Active pipeline (needs action) ───────────────────────────────────────
    active = [l for l in leads if l["stage"] not in ("Won", "Lost")]
    active.sort(key=lambda x: STAGE_RANK.get(x["stage"], 0), reverse=True)

    lines += ["## Full Lead Tracker", ""]
    lines += ["| Business | City | Niche | Stage | Value | Next Action | Contact |",
              "|---|---|---|---|---|---|---|"]
    for lead in active:
        lines.append(
            f"| {lead['business']} | {lead['city']} | {lead['niche']} "
            f"| {lead['stage']} | {lead['value']} | {lead['next_action']} | {lead['contact']} |"
        )
    lines.append("")

    # ── Won / Lost ───────────────────────────────────────────────────────────
    won  = [l for l in leads if l["stage"] == "Won"]
    lost = [l for l in leads if l["stage"] == "Lost"]
    if won:
        lines += ["## Won This Month", ""]
        for l in won:
            lines.append(f"- **{l['business']}** ({l['city']}) — {l['value']} — {l['notes']}")
        lines.append("")
    if lost:
        lines += ["## Lost This Month", ""]
        for l in lost:
            lines.append(f"- {l['business']} ({l['city']}) — {l['notes'] or 'no reason logged'}")
        lines.append("")

    # ── Executive summary ────────────────────────────────────────────────────
    total_contacted = sum(stage_counts[s] for s in STAGES if s != "Found")
    reply_count = sum(stage_counts[s] for s in ["Replied","Warm","Call Booked","Proposal Sent","Won"])
    reply_rate = f"{reply_count/total_contacted*100:.0f}%" if total_contacted else "—"
    best_niche = max(niches.items(), key=lambda x: x[1]["warm"])[0] if niches else "—"
    best_city  = top_cities[0][0] if top_cities else "—"

    lines += [
        "## Executive Summary",
        "",
        f"{month_name}: {len(leads)} leads tracked across "
        f"{len(cities)} cities. {total_contacted} contacted, "
        f"{reply_count} replied ({reply_rate} reply rate). "
        f"{stage_counts['Warm']} warm leads, "
        f"{stage_counts['Call Booked']} calls booked, "
        f"{stage_counts['Won']} won. "
        f"Pipeline forecast: ${forecast_low:,.0f}–${forecast_high:,.0f}. "
        f"Best niche: {best_niche}. Best city: {best_city}.",
        "",
    ]

    return "\n".join(lines)


def main():
    today = datetime.date.today()
    # default to previous month if run on the 1st, else current month
    if today.day == 1:
        first = today.replace(day=1) - datetime.timedelta(days=1)
        year, month = first.year, first.month
    else:
        year, month = today.year, today.month

    if len(sys.argv) == 3:
        year, month = int(sys.argv[1]), int(sys.argv[2])

    files = sorted(glob.glob("crm/week-*.md"))
    monthly_files = [f for f in files if iso_week_in_month(f, year, month)]

    if not monthly_files:
        print(f"No CRM week files found for {year}-{month:02d}", file=sys.stderr)
        sys.exit(0)

    print(f"Merging {len(monthly_files)} week files for "
          f"{datetime.date(year, month, 1).strftime('%B %Y')}", file=sys.stderr)

    all_leads = []
    for f in monthly_files:
        all_leads.extend(parse_week_file(f))

    leads = deduplicate(all_leads)
    report = build_report(leads, year, month)

    os.makedirs("crm", exist_ok=True)
    filename = f"crm/monthly-{year}-{month:02d}.md"
    with open(filename, "w") as f:
        f.write(report)

    print(f"Saved: {filename}", file=sys.stderr)
    print(filename)


if __name__ == "__main__":
    main()
