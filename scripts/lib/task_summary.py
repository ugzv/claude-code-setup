"""
Task summary extraction helpers for completion notifications.
"""

import json

from .message_cleanup import (
    clean_message_for_notification,
    detect_action_emoji,
    find_content_line,
    should_skip_line,
)
from .platform_runtime import log_debug
from .transcript_io import read_last_lines


def get_task_summary(transcript_path: str, debug_log_path=None) -> str:
    """Extract a one-line summary from the last assistant text message."""
    try:
        lines = read_last_lines(transcript_path, 50)
        if not lines:
            return "Task completed"

        for line in reversed(lines):
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            message = entry.get("message", {})
            if message.get("role") != "assistant":
                continue

            content = message.get("content", [])
            if not isinstance(content, list):
                continue

            for block in content:
                if not isinstance(block, dict) or block.get("type") != "text":
                    continue

                text = block.get("text", "").strip()
                if not text:
                    continue

                text_lines = [entry.strip() for entry in text.split("\n") if entry.strip()]
                if not text_lines:
                    continue

                first_line = text_lines[0]
                next_line_index = 1

                if len(text_lines) > 1 and should_skip_line(first_line):
                    content_line, next_line_index = find_content_line(text_lines, 1)
                    if content_line:
                        first_line = content_line
                    elif len(text_lines) > 1:
                        first_line = text_lines[1]

                if len(first_line) < 15 and next_line_index < len(text_lines):
                    second_line, _ = find_content_line(text_lines, next_line_index)
                    if second_line:
                        first_line = f"{first_line} {second_line}"

                cleaned = clean_message_for_notification(first_line)
                emoji = detect_action_emoji(cleaned)
                return f"{emoji} {cleaned}" if emoji else cleaned
    except Exception as exc:
        log_debug(f"  → Exception in get_task_summary: {exc}", path=debug_log_path)

    return "Task completed"
