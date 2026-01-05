#!/usr/bin/env bash
set -euo pipefail

if ! command -v vhs >/dev/null 2>&1; then
  echo "vhs is not installed. Install it with: brew install vhs"
  exit 1
fi

if [[ ! -f ".env" && -z "${GEMINI_API_KEY:-}" ]]; then
  echo "GEMINI_API_KEY is not set. Add it to .env or export it before recording."
  exit 1
fi

mkdir -p docs
export VHS_NO_SANDBOX=1
vhs docs/demo.tape
