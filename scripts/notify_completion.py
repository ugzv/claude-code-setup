#!/usr/bin/env python3
"""
Desktop notification for Claude Code completion.
Cross-platform: macOS (terminal-notifier/osascript) and Windows (toast notifications).
Shows project directory to identify which instance finished.
Designed for users running multiple Claude Code instances.
"""

import datetime
import json
import os
import sys

from lib.platform_detection import DEBUG_LOG_PATH, get_terminal_app, log_debug
from lib.text_processing import get_project_name, get_task_summary
from lib.notifications import send_notification


def main():
    """Send completion notification with project context."""
    # Read hook input from stdin
    try:
        input_data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception) as e:
        input_data = {}
        log_debug(f"{datetime.datetime.now().isoformat()} | ERROR reading stdin: {str(e)}")

    # Debug: Log what we received
    timestamp = datetime.datetime.now().isoformat()
    log_debug(f"{timestamp} | Hook input keys: {list(input_data.keys())} | Platform: {sys.platform}")
    if "transcript_path" in input_data:
        tp = input_data["transcript_path"]
        exists = os.path.exists(tp) if tp else False
        log_debug(f"  → transcript_path: {tp} (exists: {exists})")
    else:
        log_debug(f"  → NO transcript_path in input!")

    # Get current working directory
    cwd = input_data.get("cwd", os.getcwd())
    project_name, color = get_project_name(cwd)

    # Detect terminal/editor app
    terminal_name, terminal_emoji, terminal_app_name = get_terminal_app()

    # Log notification attempt
    log_debug(f"{datetime.datetime.now().isoformat()} | Sending notification | Project: {project_name} | Terminal: {terminal_name}")

    # Get task summary from transcript
    transcript_path = input_data.get("transcript_path")
    if transcript_path and os.path.exists(transcript_path):
        message = get_task_summary(transcript_path, DEBUG_LOG_PATH)
    else:
        message = "✓ Task completed"
        if not transcript_path:
            log_debug(f"  → Using generic message: No transcript_path provided")
        else:
            log_debug(f"  → Using generic message: File doesn't exist: {transcript_path}")

    # Send notification
    send_notification(
        title=f"{terminal_name} {color}",
        subtitle=project_name,
        message=message,
        app_name=terminal_app_name
    )

    sys.exit(0)


if __name__ == "__main__":
    main()
