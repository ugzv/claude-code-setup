"""Claude Code settings.json management.

Handles loading, saving, backing up, and merging the Claude Code settings
file, including hook configuration.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from .platform import (
    IS_WINDOWS,
    OUR_SCRIPTS,
    get_claude_dir,
    get_settings_path,
)


# ---------------------------------------------------------------------------
# Script / hook command helpers
# ---------------------------------------------------------------------------

def get_script_command(script_name: str) -> str:
    """Platform-appropriate command to run a script from scripts dir.

    Uses explicit python3 prefix on non-Windows for robustness (avoids
    reliance on shebang + execute bit surviving cross-platform copies).
    """
    script_path = get_claude_dir() / "scripts" / script_name
    if IS_WINDOWS:
        return f'python "{script_path}"'
    return f'python3 "{script_path}"'


def get_hook_command(hook_name: str) -> str:
    """Platform-appropriate command to run a hook script."""
    hook_path = get_claude_dir() / "hooks" / hook_name
    if IS_WINDOWS:
        return f'python "{hook_path}"'
    return f'python3 "{hook_path}"'


# ---------------------------------------------------------------------------
# Settings I/O
# ---------------------------------------------------------------------------

def load_settings() -> dict:
    settings_path = get_settings_path()
    if not settings_path.exists():
        return {}
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"WARNING: Could not parse settings.json: {e}")
        return {}


def save_settings(settings: dict) -> None:
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


def backup_settings() -> Optional[Path]:
    settings_path = get_settings_path()
    if not settings_path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = settings_path.parent / f"settings.json.backup_{timestamp}"
    shutil.copy2(settings_path, backup_path)
    return backup_path


# ---------------------------------------------------------------------------
# Hook filtering
# ---------------------------------------------------------------------------

def _filter_hooks(hook_configs: list, exclude_scripts: list) -> list:
    """Filter out hooks whose commands contain any of the exclude_scripts.

    Args:
        hook_configs: List of hook configuration dicts
        exclude_scripts: List of script names to filter out

    Returns:
        Filtered list with matching hooks removed
    """
    cleaned = []
    for config in hook_configs:
        if "hooks" in config:
            filtered = [
                h for h in config["hooks"]
                if not any(s in h.get("command", "") for s in exclude_scripts)
            ]
            if filtered:
                config["hooks"] = filtered
                cleaned.append(config)
        else:
            cleaned.append(config)
    return cleaned


# ---------------------------------------------------------------------------
# Config generation and merging
# ---------------------------------------------------------------------------

def get_full_config() -> dict:
    """Get the complete configuration to merge."""
    return {
        "attribution": {
            "commit": ""
        },
        "statusLine": {
            "type": "command",
            "command": get_script_command("statusline.py")
        },
        "hooks": {
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": get_hook_command("session-start.py"),
                            "timeout": 5
                        }
                    ]
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": get_script_command("stop_hook.py"),
                            "timeout": 5
                        }
                    ]
                }
            ]
        }
    }


def merge_settings(existing: dict, new_config: dict) -> dict:
    """Merge new config into existing, preserving unrelated settings."""
    settings = existing.copy()

    # Merge attribution
    if "attribution" in new_config:
        settings["attribution"] = new_config["attribution"]

    # Merge statusLine
    if "statusLine" in new_config:
        settings["statusLine"] = new_config["statusLine"]

    # Merge hooks
    if "hooks" in new_config:
        if "hooks" not in settings:
            settings["hooks"] = {}

        for hook_type, hook_configs in new_config["hooks"].items():
            if hook_type not in settings["hooks"]:
                settings["hooks"][hook_type] = hook_configs
            else:
                existing_hooks = settings["hooks"][hook_type]
                # Remove old versions of our hooks before adding new ones
                cleaned = _filter_hooks(existing_hooks, OUR_SCRIPTS)
                settings["hooks"][hook_type] = cleaned + hook_configs

    return settings


def remove_our_hooks(existing: dict) -> dict:
    """Remove our hooks from settings."""
    settings = existing.copy()
    if "hooks" not in settings:
        return settings

    for hook_type in list(settings["hooks"].keys()):
        existing_hooks = settings["hooks"][hook_type]
        cleaned = _filter_hooks(existing_hooks, OUR_SCRIPTS)

        if cleaned:
            settings["hooks"][hook_type] = cleaned
        else:
            del settings["hooks"][hook_type]

    if not settings["hooks"]:
        del settings["hooks"]

    return settings
