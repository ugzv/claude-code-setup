"""Claude Code Statusline — cross-platform, no external dependencies.

Reads JSON from stdin, outputs: model │ branch │ ●●●●○○○○○○ 42%
Color shifts at 60/75/90% context usage.
"""

import json
import subprocess
import sys


# ANSI codes
RESET = "\033[0m"
BOLD = "\033[1m"
YELLOW = "\033[33m"
RED = "\033[31m"


def get_git_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return

    # Parse model and context usage
    model_info = data.get("model") or {}
    model = model_info.get("display_name", "claude") if isinstance(model_info, dict) else "claude"
    ctx = data.get("context_window") or {}
    percent = int(ctx.get("used_percentage") or 0)

    branch = get_git_branch()

    # Build progress bar (10 dots)
    filled = min(percent // 10, 10)
    bar = "●" * filled + "○" * (10 - filled)

    # Color based on usage
    if percent >= 90:
        color = RED
    elif percent >= 75:
        color = YELLOW
    elif percent >= 60:
        color = BOLD
    else:
        color = ""

    # Output
    parts = [model]
    if branch:
        parts.append(branch)
    parts.append(f"{color}{bar}  {percent}%{RESET}" if color else f"{bar}  {percent}%")

    sys.stdout.write(" │ ".join(parts))


if __name__ == "__main__":
    main()
