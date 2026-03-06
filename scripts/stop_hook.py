#!/usr/bin/env python3
"""
Unified Stop/Notification hook for Claude Code and Codex CLI.
Replaces the sequential play_sound.py + notify_completion.py with a single process.

Performance: ~50-100ms total.
Previously: 2-4 seconds (two Python processes, each spawning PowerShell).

Supports both:
- Claude Code: Stop hook (reads transcript_path from stdin JSON)
- Codex CLI: notify hook (reads last-assistant-message from stdin JSON)

Flow:
1. Play completion sound immediately (afplay/winsound async = instant)
2. Read stdin for hook data
3. Debounce: skip if last notification was <10s ago
4. Fire-and-forget the toast notification (Popen, don't wait)
"""

import datetime
import json
import os
import sys
import time
from pathlib import Path

from sound_player import get_sound, play_sound
from lib.platform_runtime import CLI_HOME, DEBUG_LOG_PATH, log_debug
from lib.terminal_app_detection import get_terminal_app
from lib.text_processing import get_project_name, get_task_summary
from lib.notifications import send_notification_async

# Debounce: minimum seconds between notifications
# Each CLI gets its own debounce file (derived from script location)
DEBOUNCE_SECONDS = 10
_DEBOUNCE_FILE = CLI_HOME / ".last_notification_ts"


def _should_debounce() -> bool:
    """Check if we should skip notification due to debounce window."""
    try:
        if _DEBOUNCE_FILE.exists():
            with open(_DEBOUNCE_FILE, "r", encoding="utf-8") as f:
                last_ts = float(f.read().strip())
            if time.time() - last_ts < DEBOUNCE_SECONDS:
                return True
    except Exception:
        pass
    return False


def _update_debounce() -> None:
    """Record current timestamp for debounce tracking."""
    try:
        with open(_DEBOUNCE_FILE, "w", encoding="utf-8") as f:
            f.write(str(time.time()))
    except Exception:
        pass


def _load_input_data() -> dict:
    """Read hook input from stdin, defaulting to an empty payload on failure."""
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def _get_completion_message(input_data: dict) -> str:
    """Build the notification message for either Claude Code or Codex CLI."""
    transcript_path = input_data.get("transcript_path")
    if transcript_path and Path(transcript_path).exists():
        return get_task_summary(transcript_path, DEBUG_LOG_PATH)

    assistant_message = input_data.get("last-assistant-message")
    if assistant_message:
        message = str(assistant_message)
        lines = [line.strip() for line in message.split("\n") if line.strip()]
        return lines[0][:120] if lines else "Task completed"

    return "Task completed"


def _build_notification_context(input_data: dict) -> tuple[str, str, str, str]:
    """Resolve project and terminal metadata for the notification."""
    cwd = input_data.get("cwd", os.getcwd())
    project_name, color = get_project_name(cwd)
    terminal_name, _terminal_emoji, terminal_app_name = get_terminal_app()
    return project_name, color, terminal_name, terminal_app_name


def main() -> None:
    # 1. Play sound immediately (async/non-blocking)
    play_sound(get_sound("completion"))

    # 2. Read hook input from stdin
    input_data = _load_input_data()

    timestamp = datetime.datetime.now().isoformat()
    log_debug(f"{timestamp} | stop_hook | keys: {list(input_data.keys())}")

    # 3. Debounce — skip if recent notification
    if _should_debounce():
        log_debug("  → Debounced, skipping notification")
        return

    # 4. Build notification content
    project_name, color, terminal_name, terminal_app_name = _build_notification_context(
        input_data
    )
    message = _get_completion_message(input_data)

    log_debug(
        f"  → Sending async notification | Project: {project_name} | Terminal: {terminal_name}"
    )

    # 5. Fire-and-forget notification
    send_notification_async(
        title=f"{terminal_name} {color}",
        subtitle=project_name,
        message=message,
        app_name=terminal_app_name,
    )

    _update_debounce()


if __name__ == "__main__":
    main()
