#!/usr/bin/env python3
"""Cross-platform SessionStart hook for Claude Code.

Outputs state.json and handoffs.json contents on session start.
Handles missing files gracefully without errors.
"""

import sys
from pathlib import Path

# Ensure UTF-8 stdout for Unicode characters (arrows, emoji, etc.)
# Windows defaults to cp1252, and some Linux locales may not be UTF-8
if hasattr(sys.stdout, "buffer"):
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


PRIMARY_STATE_PATH = Path(".state/state.json")
LEGACY_STATE_PATH = Path(".claude/state.json")
PRIMARY_HANDOFFS_PATH = Path(".state/handoffs.json")
LEGACY_HANDOFFS_PATH = Path(".claude/handoffs.json")


def read_file(path: Path) -> str | None:
    """Read file if exists, return None otherwise."""
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except Exception:
        pass
    return None


def resolve_path(primary: Path, legacy: Path) -> Path:
    """Prefer the new shared state path, but keep legacy fallback during migration."""
    if primary.exists():
        return primary
    if legacy.exists():
        return legacy
    return primary


def main() -> None:
    # State file
    state_path = resolve_path(PRIMARY_STATE_PATH, LEGACY_STATE_PATH)
    state_content = read_file(state_path)
    if state_content:
        print(f"=== {state_path.as_posix()} ===")
        print(state_content)
    else:
        print(f"=== {PRIMARY_STATE_PATH.as_posix()} ===")
        print('{"note": "No state.json found. Run /migrate to set up tracking."}')

    # Handoffs file
    handoffs_path = resolve_path(PRIMARY_HANDOFFS_PATH, LEGACY_HANDOFFS_PATH)
    handoffs_content = read_file(handoffs_path)
    if handoffs_content:
        print(f"=== {handoffs_path.as_posix()} ===")
        print(handoffs_content)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail silently - don't break session start
        print(f"=== {PRIMARY_STATE_PATH.as_posix()} ===")
        print('{"note": "Hook error"}')
        sys.exit(0)  # Exit cleanly even on error
