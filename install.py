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
from typing import Optional

# Note: Duplicated from scripts/lib/platform_detection.py for standalone installer use
IS_WINDOWS = platform.system() == "Windows"
IS_MACOS = platform.system() == "Darwin"

# Scripts we install as hooks - used for filtering during merge/uninstall
OUR_SCRIPTS = ["play_sound.py", "notify_completion.py", "stop_hook.py", "session-start.py"]


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
    """Platform-appropriate command to run a script from scripts dir."""
    scripts_dir = get_claude_dir() / "scripts"
    script_path = scripts_dir / script_name
    if IS_WINDOWS:
        return f'python "{script_path}"'
    return str(script_path)


def get_hook_command(hook_name: str) -> str:
    """Platform-appropriate command to run a hook script."""
    hooks_dir = get_claude_dir() / "hooks"
    hook_path = hooks_dir / hook_name
    if IS_WINDOWS:
        return f'python "{hook_path}"'
    return f'python3 "{hook_path}"'


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


def backup_settings() -> Optional[Path]:
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


def copy_files(
    source_dir: Path,
    dest_dir: Path,
    pattern: str,
    dry_run: bool = False,
    make_executable: bool = False,
    remove_obsolete: bool = False,
    prefix: str = ""
) -> int:
    """
    Generic file copy function.

    Args:
        source_dir: Source directory to copy from
        dest_dir: Destination directory to copy to
        pattern: Glob pattern for files to copy (e.g., "*.md", "*.py")
        dry_run: If True, only print what would be done
        make_executable: If True, set executable permissions on copied files (Unix only)
        remove_obsolete: If True, remove files in dest that don't exist in source
        prefix: Optional prefix for log messages (e.g., "lib/")

    Returns:
        Number of files copied
    """
    if not source_dir.exists():
        return 0

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)

    # Clean obsolete files if requested
    if remove_obsolete and dest_dir.exists():
        for existing in dest_dir.glob(pattern):
            if not (source_dir / existing.name).exists():
                if dry_run:
                    print(f"  Would remove obsolete: {prefix}{existing.name}")
                else:
                    existing.unlink()
                    print(f"  Removed obsolete: {prefix}{existing.name}")

    # Copy files
    copied = 0
    for src_file in source_dir.glob(pattern):
        target = dest_dir / src_file.name
        if dry_run:
            print(f"  Would copy: {prefix}{src_file.name}")
        else:
            shutil.copy2(src_file, target)
            if make_executable and not IS_WINDOWS:
                target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        copied += 1

    return copied


def _copy_lib_subdir(source: Path, dest: Path, dry_run: bool = False) -> int:
    """
    Copy lib/ subdirectory for scripts.

    Args:
        source: Source scripts directory
        dest: Destination scripts directory
        dry_run: If True, only print what would be done

    Returns:
        Number of files copied from lib/
    """
    lib_source = source / "lib"
    lib_dest = dest / "lib"

    if not lib_source.exists():
        return 0

    return copy_files(
        source_dir=lib_source,
        dest_dir=lib_dest,
        pattern="*.py",
        dry_run=dry_run,
        make_executable=False,
        remove_obsolete=False,
        prefix="lib/"
    )


def copy_commands(dry_run: bool = False) -> int:
    """Copy command files to ~/.claude/commands/"""
    repo_dir = get_repo_dir()
    source = repo_dir / "commands"
    dest = get_claude_dir() / "commands"

    if not source.exists():
        print(f"  WARNING: Commands directory not found: {source}")
        return 0

    return copy_files(
        source_dir=source,
        dest_dir=dest,
        pattern="*.md",
        dry_run=dry_run,
        make_executable=False,
        remove_obsolete=True
    )


def copy_templates(dry_run: bool = False) -> int:
    """Copy template files to ~/.claude/templates/"""
    repo_dir = get_repo_dir()
    source = repo_dir / "templates"
    dest = get_claude_dir() / "templates"

    return copy_files(
        source_dir=source,
        dest_dir=dest,
        pattern="*.md",
        dry_run=dry_run,
        make_executable=False,
        remove_obsolete=False
    )


def copy_scripts(dry_run: bool = False) -> int:
    """Copy notification scripts to ~/.claude/scripts/"""
    repo_dir = get_repo_dir()
    source = repo_dir / "scripts"
    dest = get_claude_dir() / "scripts"

    if not source.exists():
        print(f"  WARNING: Scripts directory not found: {source}")
        return 0

    # Copy root-level Python scripts
    copied = copy_files(
        source_dir=source,
        dest_dir=dest,
        pattern="*.py",
        dry_run=dry_run,
        make_executable=True,
        remove_obsolete=False
    )

    # Copy lib/ subdirectory
    copied += _copy_lib_subdir(source, dest, dry_run)

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


def copy_hooks(dry_run: bool = False) -> int:
    """Copy hook scripts to ~/.claude/hooks/"""
    repo_dir = get_repo_dir()
    source = repo_dir / "hooks"
    dest = get_claude_dir() / "hooks"

    if not source.exists():
        return 0

    return copy_files(
        source_dir=source,
        dest_dir=dest,
        pattern="*.py",
        dry_run=dry_run,
        make_executable=True,
        remove_obsolete=False
    )


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

    # Step 6: Copy hooks
    print("Step 6: Installing hooks...")
    hook_count = copy_hooks(dry_run)
    if not dry_run:
        print(f"  {hook_count} hooks installed")
    print()

    # Step 7: Load and backup settings
    print("Step 7: Loading settings...")
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

    # Step 8: Merge settings
    print("Step 8: Merging configuration...")
    new_config = get_full_config()
    merged = merge_settings(settings, new_config)

    if dry_run:
        print("  Would configure: attribution, statusLine, SessionStart/Stop hooks")
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
        print("Commands: /migrate, /think, /handoff, /commit, /push, /fix,")
        print("          /test, /health, /analyze, /ux, /backlog, /agent,")
        print("          /dev, /commands, /prompt-guide")
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
        print("  Would remove: stop_hook.py, play_sound.py, notify_completion.py hooks")
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
