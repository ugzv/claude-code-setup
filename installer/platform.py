"""Platform detection and path constants.

Note: Platform detection is duplicated from scripts/lib/platform_detection.py
for standalone installer use.  We use sys.platform instead of platform.system()
to avoid the WMI deadlock on Python 3.13+.
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
IS_WSL = False
if sys.platform == "linux":
    try:
        IS_WSL = "microsoft" in Path("/proc/version").read_text().lower()
    except Exception:
        pass
PLATFORM_NAME = (
    "WSL"
    if IS_WSL
    else "Windows" if IS_WINDOWS else "macOS" if IS_MACOS else sys.platform
)

# ---------------------------------------------------------------------------
# Scripts we install as hooks — used for filtering during merge/uninstall
# ---------------------------------------------------------------------------
OUR_SCRIPTS = [
    "play_sound.py",
    "notify_completion.py",
    "stop_hook.py",
    "session-start.py",
]

# ---------------------------------------------------------------------------
# CLI configuration for multi-CLI support
# ---------------------------------------------------------------------------
CLI_INFO = {
    "claude": {"name": "Claude Code", "home": ".claude", "commands_subdir": "commands"},
    "codex": {"name": "Codex CLI", "home": ".codex", "commands_subdir": "prompts"},
}


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
def get_cli_dir(cli: str) -> Path:
    """Get the home directory for a CLI tool."""
    return Path.home() / CLI_INFO[cli]["home"]


def get_claude_dir() -> Path:
    return Path.home() / ".claude"


def get_repo_dir() -> Path:
    # install.py lives at repo root; this module lives one level deeper.
    return Path(__file__).parent.parent.resolve()


def get_settings_path() -> Path:
    return get_claude_dir() / "settings.json"
