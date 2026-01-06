#!/usr/bin/env python3
"""
Claude Code Setup Installer
https://github.com/ugzv/claude-code-setup

Cross-platform installer that:
- Copies commands to ~/.claude/commands/
- Copies notification scripts to ~/.claude/scripts/
- Copies templates to ~/.claude/templates/
- Installs statusline
- Safely merges settings (hooks, attribution, statusline)

Usage:
    python install.py           # Install everything
    python install.py --dry-run # Preview changes
    python install.py --uninstall # Remove hooks (keeps commands/scripts)
"""

import json
import shutil
import subprocess
import sys
import platform
import stat
import argparse
from pathlib import Path
from datetime import datetime

IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"


def install_macos_deps(dry_run: bool = False) -> None:
    """Install terminal-notifier on macOS if brew is available."""
    if not IS_MACOS:
        return

    # Check if terminal-notifier already installed
    result = subprocess.run(
        ["which", "terminal-notifier"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  terminal-notifier already installed")
        return

    # Check if brew is available
    result = subprocess.run(
        ["which", "brew"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("  terminal-notifier not found (optional, using osascript fallback)")
        print("  Install with: brew install terminal-notifier")
        return

    # Install via brew
    if dry_run:
        print("  Would install: terminal-notifier (via brew)")
    else:
        print("  Installing terminal-notifier...")
        result = subprocess.run(
            ["brew", "install", "terminal-notifier"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("  terminal-notifier installed")
        else:
            print("  Failed to install terminal-notifier (notifications will use fallback)")
            print(f"  Error: {result.stderr.strip()}")


def get_claude_dir() -> Path:
    return Path.home() / ".claude"


def get_repo_dir() -> Path:
    return Path(__file__).parent.resolve()


def get_settings_path() -> Path:
    return get_claude_dir() / "settings.json"


def get_script_command(script_name: str) -> str:
    """Platform-appropriate command to run a script."""
    scripts_dir = get_claude_dir() / "scripts"
    script_path = scripts_dir / script_name
    if IS_WINDOWS:
        return f'python "{script_path}"'
    return str(script_path)


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


def backup_settings() -> Path | None:
    settings_path = get_settings_path()
    if not settings_path.exists():
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = settings_path.parent / f"settings.json.backup_{timestamp}"
    shutil.copy2(settings_path, backup_path)
    return backup_path


def save_settings(settings: dict) -> None:
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)


def get_full_config() -> dict:
    """Get the complete configuration to merge."""
    return {
        "attribution": {
            "commit": ""
        },
        "statusLine": {
            "type": "command",
            "command": "~/.claude/statusline.sh"
        },
        "hooks": {
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": get_script_command("play_sound.py"),
                            "timeout": 5
                        },
                        {
                            "type": "command",
                            "command": get_script_command("notify_completion.py"),
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

        our_scripts = ["play_sound.py", "notify_completion.py"]

        for hook_type, hook_configs in new_config["hooks"].items():
            if hook_type not in settings["hooks"]:
                settings["hooks"][hook_type] = hook_configs
            else:
                existing_hooks = settings["hooks"][hook_type]

                # Remove old versions of our hooks
                cleaned = []
                for config in existing_hooks:
                    if "hooks" in config:
                        filtered = [
                            h for h in config["hooks"]
                            if not any(s in h.get("command", "") for s in our_scripts)
                        ]
                        if filtered:
                            config["hooks"] = filtered
                            cleaned.append(config)
                    else:
                        cleaned.append(config)

                settings["hooks"][hook_type] = cleaned + hook_configs

    return settings


def remove_our_hooks(existing: dict) -> dict:
    """Remove our hooks from settings."""
    settings = existing.copy()
    if "hooks" not in settings:
        return settings

    our_scripts = ["play_sound.py", "notify_completion.py"]

    for hook_type in list(settings["hooks"].keys()):
        existing_hooks = settings["hooks"][hook_type]
        cleaned = []

        for config in existing_hooks:
            if "hooks" in config:
                filtered = [
                    h for h in config["hooks"]
                    if not any(s in h.get("command", "") for s in our_scripts)
                ]
                if filtered:
                    config["hooks"] = filtered
                    cleaned.append(config)
            else:
                cleaned.append(config)

        if cleaned:
            settings["hooks"][hook_type] = cleaned
        else:
            del settings["hooks"][hook_type]

    if not settings["hooks"]:
        del settings["hooks"]

    return settings


def copy_commands(dry_run: bool = False) -> int:
    """Copy command files to ~/.claude/commands/"""
    repo_dir = get_repo_dir()
    source = repo_dir / "commands"
    dest = get_claude_dir() / "commands"

    if not source.exists():
        print(f"  WARNING: Commands directory not found: {source}")
        return 0

    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    # Clean obsolete commands
    if dest.exists():
        for existing in dest.glob("*.md"):
            if not (source / existing.name).exists():
                if dry_run:
                    print(f"  Would remove obsolete: {existing.name}")
                else:
                    existing.unlink()
                    print(f"  Removed obsolete: {existing.name}")

    # Copy commands
    copied = 0
    for cmd in source.glob("*.md"):
        target = dest / cmd.name
        if dry_run:
            print(f"  Would copy: {cmd.name}")
        else:
            shutil.copy2(cmd, target)
        copied += 1

    return copied


def copy_templates(dry_run: bool = False) -> int:
    """Copy template files to ~/.claude/templates/"""
    repo_dir = get_repo_dir()
    source = repo_dir / "templates"
    dest = get_claude_dir() / "templates"

    if not source.exists():
        return 0

    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    copied = 0
    for template in source.glob("*.md"):
        target = dest / template.name
        if dry_run:
            print(f"  Would copy: {template.name}")
        else:
            shutil.copy2(template, target)
        copied += 1

    return copied


def copy_scripts(dry_run: bool = False) -> int:
    """Copy notification scripts to ~/.claude/scripts/"""
    repo_dir = get_repo_dir()
    source = repo_dir / "scripts"
    dest = get_claude_dir() / "scripts"

    if not source.exists():
        print(f"  WARNING: Scripts directory not found: {source}")
        return 0

    if not dry_run:
        dest.mkdir(parents=True, exist_ok=True)

    copied = 0

    # Copy root-level Python scripts
    for script in source.glob("*.py"):
        target = dest / script.name
        if dry_run:
            print(f"  Would copy: {script.name}")
        else:
            shutil.copy2(script, target)
            if not IS_WINDOWS:
                target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        copied += 1

    # Copy lib/ subdirectory
    lib_source = source / "lib"
    lib_dest = dest / "lib"

    if lib_source.exists():
        if not dry_run:
            lib_dest.mkdir(parents=True, exist_ok=True)

        for script in lib_source.glob("*.py"):
            target = lib_dest / script.name
            if dry_run:
                print(f"  Would copy: lib/{script.name}")
            else:
                shutil.copy2(script, target)
            copied += 1

    return copied


def copy_statusline(dry_run: bool = False) -> bool:
    """Copy statusline.sh to ~/.claude/"""
    repo_dir = get_repo_dir()
    source = repo_dir / "statusline.sh"
    dest = get_claude_dir() / "statusline.sh"

    if not source.exists():
        print(f"  WARNING: statusline.sh not found")
        return False

    if dry_run:
        print(f"  Would copy: statusline.sh")
    else:
        shutil.copy2(source, dest)
        if not IS_WINDOWS:
            dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return True


def install(dry_run: bool = False) -> bool:
    """Install everything."""
    print()
    print(f"Claude Code Setup Installer ({platform.system()})")
    print("=" * 50)
    print()

    # Step 1: Copy commands
    print("Step 1: Installing commands...")
    cmd_count = copy_commands(dry_run)
    if not dry_run:
        print(f"  {cmd_count} commands installed")
    print()

    # Step 2: Copy templates
    print("Step 2: Installing templates...")
    tpl_count = copy_templates(dry_run)
    if not dry_run:
        print(f"  {tpl_count} templates installed")
    print()

    # Step 3: Copy notification scripts
    print("Step 3: Installing notification scripts...")
    script_count = copy_scripts(dry_run)
    if not dry_run:
        print(f"  {script_count} scripts installed")
    print()

    # Step 4: Install macOS dependencies
    if IS_MACOS:
        print("Step 4: Checking macOS dependencies...")
        install_macos_deps(dry_run)
        print()

    # Step 5: Copy statusline
    print("Step 5: Installing statusline...")
    copy_statusline(dry_run)
    print()

    # Step 6: Load and backup settings
    print("Step 6: Loading settings...")
    settings = load_settings()
    if settings:
        print(f"  Found existing settings")
        if not dry_run:
            backup = backup_settings()
            if backup:
                print(f"  Backup: {backup.name}")
    else:
        print("  No existing settings, creating new")
    print()

    # Step 7: Merge settings
    print("Step 7: Merging configuration...")
    new_config = get_full_config()
    merged = merge_settings(settings, new_config)

    if dry_run:
        print("  Would configure: attribution, statusLine, Stop hooks")
        print()
        print("  Resulting settings.json:")
        print("  " + "-" * 40)
        print(json.dumps(merged, indent=2))
    else:
        save_settings(merged)
        print("  Saved settings.json")
    print()

    # Done
    print("=" * 50)
    if dry_run:
        print("DRY RUN - No changes made")
        print("Run without --dry-run to install")
    else:
        print("INSTALLED!")
        print()
        print("Commands: /migrate, /think, /commit, /push, /fix, /test,")
        print("          /health, /analyze, /backlog, /agent, /dev,")
        print("          /commands, /prompt-guide")
        print()
        print("Features: Desktop notifications on task completion")
        print("          Context usage in statusline")
        print()
        print("Next: Restart Claude Code, then run /migrate in a project")
    print()

    return True


def uninstall(dry_run: bool = False) -> bool:
    """Remove notification hooks (keeps commands and scripts)."""
    print()
    print(f"Uninstalling notification hooks ({platform.system()})")
    print("=" * 50)
    print()

    settings = load_settings()
    if not settings:
        print("No settings found. Nothing to uninstall.")
        return True

    if not dry_run:
        backup = backup_settings()
        if backup:
            print(f"Backup: {backup.name}")
        print()

    print("Removing notification hooks...")
    cleaned = remove_our_hooks(settings)

    if dry_run:
        print("  Would remove: play_sound.py, notify_completion.py hooks")
        print()
        print("  Resulting settings.json:")
        print(json.dumps(cleaned, indent=2))
    else:
        save_settings(cleaned)
        print("  Hooks removed")
    print()

    print("Note: Commands and scripts were kept.")
    print("      Delete ~/.claude/scripts/ manually if not needed.")
    print()

    if not dry_run:
        print("Restart Claude Code for changes to take effect.")
    print()

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Install Claude Code commands and notification hooks"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without making them"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove notification hooks (keeps commands/scripts)"
    )

    args = parser.parse_args()

    if args.uninstall:
        success = uninstall(args.dry_run)
    else:
        success = install(args.dry_run)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
