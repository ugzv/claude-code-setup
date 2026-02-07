#!/usr/bin/env python3
"""
Unified Stop hook for Claude Code.
Replaces the sequential play_sound.py + notify_completion.py with a single process.

Performance: ~15ms when terminal focused (common case), ~50-100ms when not.
Previously: 2-4 seconds (two Python processes, each spawning PowerShell).

Flow:
1. Play completion sound immediately (winsound async = instant)
2. Read stdin for hook data
3. Check terminal focus via ctypes — skip notification if focused
4. Debounce: skip if last notification was <10s ago
5. Fire-and-forget the toast notification (Popen, don't wait)
"""

import datetime
import json
import os
import sys
import time

from sound_player import get_sound, play_sound
from lib.platform_detection import (
    DEBUG_LOG_PATH,
    get_terminal_app, is_terminal_focused, log_debug,
)
from lib.text_processing import get_project_name, get_task_summary
from lib.notifications import send_notification_async

# Debounce: minimum seconds between notifications
DEBOUNCE_SECONDS = 10
_DEBOUNCE_FILE = os.path.join(os.path.expanduser("~"), ".claude", ".last_notification_ts")


def _should_debounce() -> bool:
    """Check if we should skip notification due to debounce window."""
    try:
        if os.path.exists(_DEBOUNCE_FILE):
            with open(_DEBOUNCE_FILE, "r") as f:
                last_ts = float(f.read().strip())
            if time.time() - last_ts < DEBOUNCE_SECONDS:
                return True
    except Exception:
        pass
    return False


def _update_debounce():
    """Record current timestamp for debounce tracking."""
    try:
        with open(_DEBOUNCE_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        pass


def main():
    # 1. Play sound immediately (async/non-blocking)
    play_sound(get_sound("completion"))

    # 2. Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except Exception:
        input_data = {}

    timestamp = datetime.datetime.now().isoformat()
    log_debug(f"{timestamp} | stop_hook | keys: {list(input_data.keys())}")

    # 3. Check terminal focus — skip notification if focused
    if is_terminal_focused():
        log_debug(f"  -> Terminal focused, skipping notification")
        return

    # 4. Debounce — skip if recent notification
    if _should_debounce():
        log_debug(f"  -> Debounced, skipping notification")
        return

    # 5. Build notification content
    cwd = input_data.get("cwd", os.getcwd())
    project_name, color = get_project_name(cwd)
    terminal_name, terminal_emoji, terminal_app_name = get_terminal_app()

    transcript_path = input_data.get("transcript_path")
    if transcript_path and os.path.exists(transcript_path):
        message = get_task_summary(transcript_path, DEBUG_LOG_PATH)
    else:
        message = "Task completed"

    log_debug(f"  -> Sending async notification | Project: {project_name} | Terminal: {terminal_name}")

    # 6. Fire-and-forget notification
    send_notification_async(
        title=f"{terminal_name} {color}",
        subtitle=project_name,
        message=message,
        app_name=terminal_app_name,
    )

    _update_debounce()


if __name__ == "__main__":
    main()
