"""
Compatibility facade for text-processing helpers.
"""

from .message_cleanup import (
    SKIP_PHRASES,
    clean_message_for_notification,
    detect_action_emoji,
    find_content_line as _find_content_line,
    should_skip_line as _should_skip_line,
)
from .project_identity import get_project_color, get_project_name
from .task_summary import get_task_summary
from .transcript_io import read_last_lines

__all__ = [
    "SKIP_PHRASES",
    "clean_message_for_notification",
    "detect_action_emoji",
    "get_project_color",
    "get_project_name",
    "get_task_summary",
    "read_last_lines",
]
