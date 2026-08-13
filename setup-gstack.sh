#!/usr/bin/env bash
# setup-gstack.sh — install gstack (Garry Tan's Claude Code skills framework)
# into ~/.claude/skills/gstack from a local zip or from GitHub.
#
# Usage:
#   ./setup-gstack.sh                 # clone from GitHub (requires network)
#   ./setup-gstack.sh /path/to.zip    # install from a local zip file
#
# Requirements: bun >=1.0, git, bash

set -euo pipefail

ZIP_PATH="${1:-}"
INSTALL_DIR="$HOME/.claude/skills/gstack"

# ── 1. Verify bun ───────────────────────────────────────────────────────────
if ! command -v bun >/dev/null 2>&1; then
  echo "Error: bun is required but not found." >&2
  echo "Install it:" >&2
  echo "  curl -fsSL https://bun.sh/install | bash" >&2
  exit 1
fi
echo "bun $(bun --version) found."

# ── 2. Acquire gstack source ─────────────────────────────────────────────────
if [ -n "$ZIP_PATH" ]; then
  if [ ! -f "$ZIP_PATH" ]; then
    echo "Error: zip file not found: $ZIP_PATH" >&2
    exit 1
  fi
  echo "Installing gstack from zip: $ZIP_PATH"
  TMP_DIR="$(mktemp -d)"
  trap 'rm -rf "$TMP_DIR"' EXIT
  unzip -q "$ZIP_PATH" -d "$TMP_DIR"
  # zip may have a single top-level directory — find the gstack root
  SRC="$(find "$TMP_DIR" -maxdepth 1 -mindepth 1 -type d | head -1)"
  if [ -z "$SRC" ]; then
    echo "Error: could not find extracted directory inside zip." >&2
    exit 1
  fi
  rm -rf "$INSTALL_DIR"
  cp -r "$SRC" "$INSTALL_DIR"
else
  echo "Cloning gstack from GitHub..."
  rm -rf "$INSTALL_DIR"
  git clone --single-branch --depth 1 \
    https://github.com/garrytan/gstack.git "$INSTALL_DIR"
fi

# ── 3. Install npm/bun dependencies ─────────────────────────────────────────
echo "Installing dependencies..."
(cd "$INSTALL_DIR" && bun install)

# ── 4. Run gstack's own setup (builds browse/design binaries, registers skills)
echo "Building binaries and registering skills..."
chmod +x "$INSTALL_DIR/setup"
chmod +x "$INSTALL_DIR/bin"/gstack-* 2>/dev/null || true
(cd "$INSTALL_DIR" && ./setup) || {
  echo ""
  echo "Note: setup exited with errors (Playwright Chromium download may be blocked"
  echo "      by network policy — /browse and /qa browser skills won't work in"
  echo "      restricted environments). All other skills are available."
}

# ── 5. Summary ────────────────────────────────────────────────────────────────
echo ""
echo "gstack installed to: $INSTALL_DIR"
echo ""
echo "Available slash commands:"
echo "  /office-hours       Product interrogation & scoping"
echo "  /plan-ceo-review    Strategic challenge, 10-section review"
echo "  /plan-eng-review    Architecture lock-down"
echo "  /plan-design-review Design critique"
echo "  /autoplan           End-to-end task planner with adversarial critique"
echo "  /review             Production-bug code review"
echo "  /ship               Full PR ship workflow (review + QA + release notes)"
echo "  /qa                 Real-browser QA on a URL"
echo "  /qa-only            QA-only pass (no review)"
echo "  /browse             Headless browser for research or site testing"
echo "  /cso                OWASP + STRIDE security audit"
echo "  /design-review      Design critique with slop detection"
echo "  /design-consultation Full design consultation"
echo "  /design-shotgun     Rapid design alternatives"
echo "  /design-html        HTML prototype from a description"
echo "  /investigate        Root-cause investigation"
echo "  /retro              Engineering retrospective"
echo "  /document-release   Release notes writer"
echo "  /document-generate  Documentation generator"
echo "  /canary             Canary deploy checker"
echo "  /land-and-deploy    Land + deploy workflow"
echo "  /setup-deploy       Wire up a deploy target"
echo "  /setup-gbrain       Wire up GBrain memory"
echo "  /benchmark          LLM benchmark runner"
echo "  /codex              OpenAI Codex task runner"
echo "  /learn              Learn from past sessions"
echo "  /careful            Careful mode (slower, more thorough)"
echo "  /freeze /unfreeze   Lock/unlock files from AI edits"
echo "  /guard              Guard a file from accidental changes"
echo "  /skillify           Turn an SOP into a SKILL.md"
echo "  /gstack-upgrade     Upgrade gstack to latest"
echo ""
echo "Reload Claude Code (or start a new session) to pick up the new skills."
