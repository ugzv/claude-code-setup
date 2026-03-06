"""
Transcript file helpers.
"""

from collections import deque


def read_last_lines(file_path: str, num_lines: int = 50) -> list[str]:
    """Read the last N lines from a file using a bounded deque."""
    try:
        with open(file_path, "rb") as handle:
            lines: deque[str] = deque(maxlen=num_lines)
            for line in handle:
                try:
                    lines.append(line.decode("utf-8"))
                except UnicodeDecodeError:
                    lines.append(line.decode("utf-8", errors="replace"))
            return list(lines)
    except Exception:
        return []
