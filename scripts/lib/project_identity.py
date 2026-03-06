"""
Project identification helpers for notifications.
"""

from pathlib import Path


def get_project_color(project_name: str) -> str:
    """Get a color emoji based on project name hash for visual differentiation."""
    colors = ["🔵", "🟢", "🟡", "🟠", "🔴", "🟣", "🟤", "⚪️"]
    hash_val = sum(ord(char) for char in project_name)
    return colors[hash_val % len(colors)]


def get_project_name(cwd: str) -> tuple[str, str]:
    """Extract a clean project name and color indicator from a path."""
    path = Path(cwd)
    project_name = path.name
    color = get_project_color(project_name)
    return project_name, color
