"""
Text processing utilities for Claude Code hooks.
Handles transcript parsing, message cleaning, and task summary extraction.
"""

import json
import re
from collections import deque
from pathlib import Path

from .platform_detection import log_debug


# =============================================================================
# Project Identification
# =============================================================================

def get_project_color(project_name: str) -> str:
    """Get a color emoji based on project name hash for visual differentiation."""
    colors = ["🔵", "🟢", "🟡", "🟠", "🔴", "🟣", "🟤", "⚪️"]
    hash_val = sum(ord(c) for c in project_name)
    return colors[hash_val % len(colors)]


def get_project_name(cwd: str) -> tuple:
    """Extract clean project name and color indicator from path."""
    path = Path(cwd)
    project_name = path.name
    color = get_project_color(project_name)
    return project_name, color


# =============================================================================
# Transcript Reading
# =============================================================================

def read_last_lines(file_path: str, num_lines: int = 50) -> list:
    """Read the last N lines from a file (pure Python, cross-platform)."""
    try:
        with open(file_path, 'rb') as f:
            # Use deque for efficient tail operation
            lines = deque(maxlen=num_lines)
            for line in f:
                try:
                    lines.append(line.decode('utf-8'))
                except UnicodeDecodeError:
                    lines.append(line.decode('utf-8', errors='replace'))
            return list(lines)
    except Exception:
        return []


# =============================================================================
# Message Cleaning
# =============================================================================

# Skip phrases for filtering acknowledgments
SKIP_PHRASES = [
    "perfect", "great", "done", "excellent", "ok", "sure",
    "got it", "understood", "alright", "absolutely",
    "you're right", "you're absolutely right", "that's right",
    "certainly", "definitely", "of course", "exactly",
    "good catch", "good point", "good question",
    "i see", "i understand", "makes sense",
    "no problem", "sounds good", "will do"
]


def detect_action_emoji(text: str) -> str:
    """Detect the type of action from the message and return appropriate emoji."""
    text_lower = text.lower()

    if any(word in text_lower for word in ['fix', 'bug', 'error', 'issue', 'resolve', 'correct']):
        return '🐛'
    if any(word in text_lower for word in ['edit', 'update', 'modify', 'change', 'improve', 'refactor']):
        return '✏️'
    if any(word in text_lower for word in ['search', 'find', 'look', 'explore', 'check', 'review']):
        return '🔍'
    if any(word in text_lower for word in ['create', 'add', 'write', 'implement', 'build']):
        return '✨'
    if any(word in text_lower for word in ['delete', 'remove', 'clean', 'clear']):
        return '🗑️'
    if any(word in text_lower for word in ['test', 'testing']):
        return '🧪'
    if any(word in text_lower for word in ['document', 'readme', 'comment']):
        return '📝'
    if any(word in text_lower for word in ['complete', 'done', 'finish', 'success']):
        return '✅'

    return ''


def clean_message_for_notification(text: str) -> str:
    """Clean and format a message for notification display."""
    # Remove markdown headers
    text = re.sub(r'^#+\s*', '', text).strip()
    # Remove markdown bold
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    # Remove markdown italic
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    # Remove markdown code backticks
    text = re.sub(r'`(.+?)`', r'\1', text)

    if len(text) <= 120:
        return text

    # Truncate at natural break points
    pattern = r'[.!?](?:\s|$)| - '
    match = re.search(pattern, text)

    if match and match.start() <= 120:
        return text[:match.start()].strip()

    return text[:117] + '...'


def _should_skip_line(first_line: str) -> bool:
    """Check if a line should be skipped (generic acknowledgment)."""
    first_line_lower = first_line.lower()
    first_word = first_line.split()[0].lower().rstrip("!.,?:;") if first_line.split() else ""

    return (
        first_word in SKIP_PHRASES or
        any(first_line_lower.startswith(phrase + " ") or
            first_line_lower.startswith(phrase + "!")
            for phrase in SKIP_PHRASES)
    )


def _find_content_line(text_lines: list, start_index: int = 0) -> tuple:
    """Find the first meaningful content line starting from index.
    Returns (line, next_index)."""
    for i in range(start_index, len(text_lines)):
        candidate = text_lines[i]
        if candidate and not candidate.startswith('#') and len(candidate.strip('*_# ')) > 0:
            return candidate, i + 1
    return None, len(text_lines)


# =============================================================================
# Task Summary Extraction
# =============================================================================

def get_task_summary(transcript_path: str, debug_log_path=None) -> str:
    """Extract one-line summary from last assistant message with text content."""
    try:
        lines = read_last_lines(transcript_path, 50)

        if not lines:
            return "Task completed"

        # Parse JSONL backwards to find the LAST assistant message with text
        for line in reversed(lines):
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
                msg = entry.get('message', {})
                if msg.get('role') != 'assistant':
                    continue

                content = msg.get('content', [])
                if isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue

                        if block.get('type') != 'text':
                            continue

                        text = block.get('text', '').strip()
                        if not text:
                            continue

                        text_lines = [l.strip() for l in text.split('\n') if l.strip()]
                        if not text_lines:
                            continue

                        first_line = text_lines[0]
                        next_line_index = 1

                        # Skip generic acknowledgments
                        if len(text_lines) > 1 and _should_skip_line(first_line):
                            content_line, next_line_index = _find_content_line(text_lines, 1)
                            if content_line:
                                first_line = content_line
                            elif len(text_lines) > 1:
                                first_line = text_lines[1]

                        # If first line is too short, combine with next
                        if len(first_line) < 15 and next_line_index < len(text_lines):
                            second_line, _ = _find_content_line(text_lines, next_line_index)
                            if second_line:
                                first_line = f"{first_line} {second_line}"

                        cleaned = clean_message_for_notification(first_line)
                        emoji = detect_action_emoji(cleaned)
                        return f"{emoji} {cleaned}" if emoji else cleaned

            except json.JSONDecodeError:
                continue

    except Exception as e:
        log_debug(f"  → Exception in get_task_summary: {str(e)}", path=debug_log_path)

    return "Task completed"
