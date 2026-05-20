#!/usr/bin/env python3
"""
One-time script: reads the NINE NotebookLM notebook and writes
knowledge/nine-brand-knowledge.md for use by the email pipeline.

Run via GitHub Actions (export-knowledge.yml) — requires
NOTEBOOKLM_STORAGE_STATE secret.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

NOTEBOOK_ID = "2d54d3d9-bc8d-42b7-8db7-1ac2dee912a7"
STORAGE_PATH = "/tmp/nlm_storage.json"
OUTPUT_FILE = "knowledge/nine-brand-knowledge.md"

QUESTIONS = [
    ("brand_identity",      "What is NINE's brand identity, mission, and positioning? What makes NINE different from other creative agencies?"),
    ("brand_voice",         "What is NINE's brand voice and tone? How should NINE sound in cold emails and outreach messages?"),
    ("content_sprint",      "What is the Content Sprint offer? What does it include, how long does it take, and what is the pricing?"),
    ("icp",                 "Who is NINE's ideal client? What industries, company sizes, and decision maker roles does NINE target?"),
    ("pitch_approach",      "What is NINE's overall pitch approach and sales philosophy? What should always be led with?"),
    ("restaurants_angle",   "What is NINE's specific pitch angle for restaurants and food & beverage businesses?"),
    ("wellness_angle",      "What is NINE's specific pitch angle for health and wellness businesses?"),
    ("fmcg_angle",          "What is NINE's specific pitch angle for FMCG and packaged goods brands?"),
    ("events_angle",        "What is NINE's specific pitch angle for event venues and wedding businesses?"),
    ("email_guidelines",    "What are the rules for writing a NINE cold email? What must always be included and what must never appear?"),
    ("email_template",      "Give a full example cold email written in NINE's voice for a restaurant with weak social media presence."),
    ("objections",          "What are the most common objections NINE gets and how should they be handled?"),
    ("services",            "What services does NINE offer beyond the Content Sprint? List all with brief descriptions."),
    ("case_studies",        "What results or case studies does NINE have that can be referenced in outreach?"),
    ("linkedin_approach",   "How should NINE approach LinkedIn outreach? What makes a good connection note and follow-up DM?"),
]


async def _query(question: str) -> str:
    from notebooklm import NotebookLMClient  # type: ignore
    async with NotebookLMClient.from_storage() as client:
        result = await client.chat.ask(NOTEBOOK_ID, question)
        return str(result)


def query(label: str, question: str) -> str:
    print(f"  Querying: {label}...", file=sys.stderr)
    try:
        result = asyncio.run(_query(question))
        print(f"  OK ({len(result)} chars)", file=sys.stderr)
        return result
    except Exception as e:
        print(f"  FAILED: {e}", file=sys.stderr)
        return "_Not available — re-run to retry._"


def build_md(answers: dict) -> str:
    lines = [
        "# NINE — Brand Knowledge Base",
        "_Auto-generated from NotebookLM. Re-run `export-knowledge.yml` to refresh._",
        "",
        "---",
        "",
    ]

    sections = [
        ("Brand Identity",          "brand_identity"),
        ("Brand Voice & Tone",      "brand_voice"),
        ("The Content Sprint Offer","content_sprint"),
        ("Ideal Client Profile",    "icp"),
        ("Pitch Approach",          "pitch_approach"),
        ("Niche: Restaurants",      "restaurants_angle"),
        ("Niche: Health & Wellness","wellness_angle"),
        ("Niche: FMCG",             "fmcg_angle"),
        ("Niche: Events & Venues",  "events_angle"),
        ("Cold Email Guidelines",   "email_guidelines"),
        ("Cold Email Example",      "email_template"),
        ("Handling Objections",     "objections"),
        ("Full Service Menu",       "services"),
        ("Case Studies & Results",  "case_studies"),
        ("LinkedIn Outreach",       "linkedin_approach"),
    ]

    for heading, key in sections:
        lines += [f"## {heading}", "", answers.get(key, "_Not available._"), "", "---", ""]

    return "\n".join(lines)


def main():
    state = os.environ.get("NOTEBOOKLM_STORAGE_STATE", "").strip()
    if not state:
        print("ERROR: NOTEBOOKLM_STORAGE_STATE not set.", file=sys.stderr)
        sys.exit(1)

    try:
        # raw_decode ignores any trailing characters after the JSON object
        decoder = json.JSONDecoder()
        parsed, _ = decoder.raw_decode(state)
        clean_state = json.dumps(parsed)
        # Write to the default profile path notebooklm-py expects
        profile_path = Path.home() / ".notebooklm" / "profiles" / "default"
        profile_path.mkdir(parents=True, exist_ok=True)
        (profile_path / "storage_state.json").write_text(clean_state)
    except Exception as e:
        print(f"ERROR: Bad storage state JSON: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Querying {len(QUESTIONS)} sections from notebook {NOTEBOOK_ID}...", file=sys.stderr)
    answers = {label: query(label, q) for label, q in QUESTIONS}

    Path("knowledge").mkdir(exist_ok=True)
    Path(OUTPUT_FILE).write_text(build_md(answers))
    print(f"Written: {OUTPUT_FILE}", file=sys.stderr)
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
