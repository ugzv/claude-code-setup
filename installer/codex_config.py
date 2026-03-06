"""Codex CLI config.toml management.

Handles reading, writing, and merging the Codex CLI notification hook
inside config.toml (basic TOML operations without a third-party library).
"""

import json
from pathlib import Path

from .platform import IS_WINDOWS, get_cli_dir


def get_codex_notify_command() -> list:
    """Get the notify command array for Codex config.toml."""
    codex_dir = get_cli_dir("codex")
    script_path = codex_dir / "scripts" / "stop_hook.py"
    # Use forward slashes for TOML compatibility (works on all platforms)
    path_str = str(script_path).replace("\\", "/")
    python_cmd = "python" if IS_WINDOWS else "python3"
    return [python_cmd, path_str]


def load_codex_config(codex_dir: Path) -> str:
    """Read existing Codex config.toml or return empty string."""
    config_path = codex_dir / "config.toml"
    if config_path.exists():
        try:
            return config_path.read_text(encoding="utf-8")
        except Exception:
            return ""
    return ""


def save_codex_config(codex_dir: Path, content: str) -> None:
    """Write Codex config.toml."""
    config_path = codex_dir / "config.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(content, encoding="utf-8")


def merge_codex_config(codex_dir: Path, dry_run: bool = False) -> None:
    """Add or update notify hook in Codex config.toml.

    IMPORTANT: The `notify` key must be at the top level of config.toml,
    NOT inside any [section]. TOML scoping means anything after a [section]
    header belongs to that section. We insert before the first section header.
    """
    notify_cmd = get_codex_notify_command()
    notify_line = f"notify = {json.dumps(notify_cmd)}"

    content = load_codex_config(codex_dir)

    if content:
        lines = content.splitlines()

        # Check if notify already exists (at top level, before any section)
        found = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Stop at first section header -- anything after is not top-level
            if stripped.startswith("["):
                break
            if stripped.startswith("notify") and "=" in stripped:
                lines[i] = notify_line
                found = True
                break

        if not found:
            # Also check inside sections (in case of previous bad install)
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith("notify") and "=" in stripped:
                    # Remove the misplaced line (and its comment)
                    if i > 0 and "claude-code-setup" in lines[i - 1]:
                        lines[i - 1] = ""
                        if i > 1 and lines[i - 2].strip() == "":
                            lines[i - 2] = ""
                    lines[i] = ""
                    break

            # Insert at top level: find the first [section] and insert before it
            insert_at = len(lines)
            for i, line in enumerate(lines):
                if line.strip().startswith("["):
                    insert_at = i
                    break

            comment = "# Task completion notifications (claude-code-setup)"
            lines.insert(insert_at, "")
            lines.insert(insert_at, notify_line)
            lines.insert(insert_at, comment)

        # Clean up excess blank lines
        new_content = "\n".join(lines).rstrip() + "\n"
    else:
        new_content = (
            "# Codex CLI configuration\n"
            "# Notification hook installed by claude-code-setup\n\n"
            f"{notify_line}\n"
        )

    if dry_run:
        print("  Would configure: notify hook in config.toml")
    else:
        save_codex_config(codex_dir, new_content)
        print("  Saved config.toml")


def remove_codex_notify(codex_dir: Path, dry_run: bool = False) -> None:
    """Remove notify hook from Codex config.toml."""
    content = load_codex_config(codex_dir)
    if not content:
        print("  No config.toml found. Nothing to remove.")
        return

    lines = content.splitlines()
    new_lines = []
    removed = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Skip the notify line and its comment
        if stripped.startswith("notify") and "=" in stripped:
            # Also remove preceding comment if it's ours
            if new_lines and "claude-code-setup" in new_lines[-1]:
                new_lines.pop()
                if new_lines and new_lines[-1].strip() == "":
                    new_lines.pop()
            removed = True
            continue
        new_lines.append(line)

    if removed:
        new_content = "\n".join(new_lines).rstrip() + "\n"
        if dry_run:
            print("  Would remove: notify hook from config.toml")
        else:
            save_codex_config(codex_dir, new_content)
            print("  Removed notify hook from config.toml")
    else:
        print("  No notify hook found in config.toml")
