#!/usr/bin/env python3
"""
Queries the NINE NotebookLM notebook for pitch context and brand knowledge.

Used by analyze_leads.py before drafting email hooks.
Also available as a general-purpose knowledge utility for any NINE script.

Requires: NOTEBOOKLM_STORAGE_STATE env var (full JSON from storage_state.json)
Falls back silently to "" on any failure — never breaks the main pipeline.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

NOTEBOOK_ID = "2d54d3d9-bc8d-42b7-8db7-1ac2dee912a7"
_STORAGE_PATH = "/tmp/nlm_storage.json"
_cache: dict[str, str] = {}


def _write_storage_state() -> bool:
    state = os.environ.get("NOTEBOOKLM_STORAGE_STATE", "").strip()
    if not state:
        print("  [NotebookLM] NOTEBOOKLM_STORAGE_STATE not set — skipping", file=sys.stderr)
        return False
    try:
        # raw_decode ignores any trailing characters after the JSON object
        decoder = json.JSONDecoder()
        parsed, _ = decoder.raw_decode(state)
        clean_state = json.dumps(parsed)
        # Write to the default profile path notebooklm-py expects
        profile_path = Path.home() / ".notebooklm" / "profiles" / "default"
        profile_path.mkdir(parents=True, exist_ok=True)
        (profile_path / "storage_state.json").write_text(clean_state)
        return True
    except Exception as e:
        print(f"  [NotebookLM] Bad storage state JSON: {e}", file=sys.stderr)
        return False


async def _async_query(question: str) -> str:
    from notebooklm import NotebookLMClient  # type: ignore
    async with await NotebookLMClient.from_storage() as client:
        result = await client.chat.ask(NOTEBOOK_ID, question)
        return getattr(result, "answer", None) or getattr(result, "text", None) or str(result)


def query(question: str) -> str:
    """
    Query the NINE NotebookLM. Returns answer string or "" on any failure.
    Results are cached in memory — same question is never asked twice per run.
    """
    if question in _cache:
        return _cache[question]

    if not _write_storage_state():
        return ""

    try:
        result = asyncio.run(_async_query(question))
        _cache[question] = result
        print(f"  [NotebookLM] OK — {len(result)} chars returned", file=sys.stderr)
        return result
    except Exception as e:
        print(f"  [NotebookLM] query failed: {e}", file=sys.stderr)
        return ""


# ── Pre-built queries for the email pipeline ─────────────────────────────────

def get_email_hook(niche: str, city: str, weakness: str) -> str:
    """
    2-sentence opening hook for a cold email, written in NINE's voice.
    Returns "" if NotebookLM is unavailable.
    """
    return query(
        f"Write a 2-sentence cold email opening hook for a {niche} business in {city}. "
        f"Their main digital weakness is: {weakness}. "
        f"Use NINE's brand voice and Content Sprint pitch. "
        f"Be direct and specific — no fluff, no greetings, no sign-off."
    )


def get_pitch_guidelines() -> str:
    """
    General NINE pitch guidelines fetched from the notebook.
    Call once at the start of a run and reuse — result is cached.
    """
    return query(
        "Summarise NINE agency's pitch approach, brand voice, Content Sprint offer, "
        "and ideal client profile in 4-5 sentences. "
        "This will be injected into cold email drafts."
    )


def get_niche_angle(niche: str) -> str:
    """Niche-specific pitch angle from the NINE notebook."""
    return query(
        f"What is NINE's specific pitch angle and value proposition for the {niche} industry? "
        f"Answer in 2 sentences maximum."
    )
