"""
Notification message cleanup helpers.
"""

import re


SKIP_PHRASES = [
    "perfect", "great", "done", "excellent", "ok", "sure",
    "got it", "understood", "alright", "absolutely",
    "you're right", "you're absolutely right", "that's right",
    "certainly", "definitely", "of course", "exactly",
    "good catch", "good point", "good question",
    "i see", "i understand", "makes sense",
    "no problem", "sounds good", "will do",
]


def detect_action_emoji(text: str) -> str:
    """Detect the type of action from a message and return an emoji."""
    text_lower = text.lower()

    if any(word in text_lower for word in ["fix", "bug", "error", "issue", "resolve", "correct"]):
        return "🐛"
    if any(word in text_lower for word in ["edit", "update", "modify", "change", "improve", "refactor"]):
        return "✏️"
    if any(word in text_lower for word in ["search", "find", "look", "explore", "check", "review"]):
        return "🔍"
    if any(word in text_lower for word in ["create", "add", "write", "implement", "build"]):
        return "✨"
    if any(word in text_lower for word in ["delete", "remove", "clean", "clear"]):
        return "🗑️"
    if any(word in text_lower for word in ["test", "testing"]):
        return "🧪"
    if any(word in text_lower for word in ["document", "readme", "comment"]):
        return "📝"
    if any(word in text_lower for word in ["complete", "done", "finish", "success"]):
        return "✅"

    return ""


def clean_message_for_notification(text: str) -> str:
    """Clean and format a message for notification display."""
    text = re.sub(r"^#+\s*", "", text).strip()
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)

    if len(text) <= 120:
        return text

    match = re.search(r"[.!?](?:\s|$)| - ", text)
    if match and match.start() <= 120:
        return text[:match.start()].strip()

    return text[:117] + "..."


def should_skip_line(first_line: str) -> bool:
    """Check if a line is just a generic acknowledgment."""
    first_line_lower = first_line.lower()
    words = first_line.split()
    first_word = words[0].lower().rstrip("!.,?:;") if words else ""

    return first_word in SKIP_PHRASES or any(
        first_line_lower.startswith(phrase + " ") or first_line_lower.startswith(phrase + "!")
        for phrase in SKIP_PHRASES
    )


def find_content_line(text_lines: list[str], start_index: int = 0) -> tuple[str | None, int]:
    """Find the first non-empty, non-heading line starting at an index."""
    for index in range(start_index, len(text_lines)):
        candidate = text_lines[index]
        if candidate and not candidate.startswith("#") and len(candidate.strip("*_# ")) > 0:
            return candidate, index + 1
    return None, len(text_lines)
