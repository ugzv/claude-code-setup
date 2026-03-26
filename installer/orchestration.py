"""Install / uninstall orchestration and CLI entry point.

This module wires together all the sub-modules and provides the public
install(), install_codex(), uninstall(), uninstall_codex() functions as
well as the main() CLI entry point.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .platform import (
    IS_MACOS,
    IS_WINDOWS,
    IS_WSL,
    PLATFORM_NAME,
    get_cli_dir,
)
from .deps import install_macos_deps, install_wsl_deps
from .claude_settings import (
    backup_settings,
    get_full_config,
    load_settings,
    merge_settings,
    remove_our_hooks,
    save_settings,
)
from .codex_config import merge_codex_config, remove_codex_notify
from .file_ops import (
    run_install_steps,
)

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------


def install(dry_run: bool = False) -> bool:
    """Install everything for Claude Code."""
    print()
    print(f"Claude Code Setup Installer ({PLATFORM_NAME})")
    print("=" * 50)
    print()

    run_install_steps("claude", dry_run=dry_run, only_steps=(1, 2, 3))

    # Step 4: Platform dependencies
    if IS_MACOS:
        print("Step 4: Checking macOS dependencies...")
        install_macos_deps(dry_run)
        print()
    elif IS_WSL or not IS_WINDOWS:
        print("Step 4: Checking Linux/WSL dependencies...")
        install_wsl_deps(dry_run)
        print()

    run_install_steps("claude", dry_run=dry_run, only_steps=(5,))

    # Step 6: Load and backup settings
    print("Step 6: Loading settings...")
    settings = load_settings()
    if settings:
        print("  Found existing settings")
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
        print("          /test, /health, /analyze, /dedup, /ux, /backlog,")
        print("          /agent, /dev, /commands, /prompt-guide")
        print()
        print("Features: Desktop notifications on task completion")
        print("          Context usage in statusline")
        print()
        print("Next: Restart Claude Code, then run /migrate in a project")
    print()

    return True


def install_codex(dry_run: bool = False) -> bool:
    """Install commands and notifications for Codex CLI."""
    codex_dir = get_cli_dir("codex")

    print()
    print(f"Codex CLI Setup ({PLATFORM_NAME})")
    print("=" * 50)
    print()

    run_install_steps("codex", dry_run=dry_run, only_steps=(1, 2, 3))

    # Step 4: Platform dependencies
    if IS_MACOS:
        print("Step 4: Checking macOS dependencies...")
        install_macos_deps(dry_run)
        print()
    elif IS_WSL or not IS_WINDOWS:
        print("Step 4: Checking Linux/WSL dependencies...")
        install_wsl_deps(dry_run)
        print()

    # Step 5: Configure notify in config.toml
    print("Step 5: Configuring notifications...")
    merge_codex_config(codex_dir, dry_run)
    print()

    # Done
    print("=" * 50)
    if dry_run:
        print("DRY RUN - No changes made")
        print("Run without --dry-run to install")
    else:
        print("INSTALLED for Codex CLI!")
        print()
        print("Commands available as /command-name in Codex interactive mode")
        print()
        print("Features: Desktop notifications on task completion")
        print()
        print("Note: SessionStart hooks and statusline are Claude Code only")
        print("Next: Restart Codex CLI, use AGENTS.md template for new projects")
    print()

    return True


# ---------------------------------------------------------------------------
# Uninstall
# ---------------------------------------------------------------------------


def uninstall(dry_run: bool = False) -> bool:
    """Remove notification hooks from Claude Code (keeps commands and scripts)."""
    print()
    print(f"Uninstalling Claude Code hooks ({PLATFORM_NAME})")
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


def uninstall_codex(dry_run: bool = False) -> bool:
    """Remove notify hook from Codex CLI (keeps commands and scripts)."""
    codex_dir = get_cli_dir("codex")

    print()
    print(f"Uninstalling Codex CLI hooks ({PLATFORM_NAME})")
    print("=" * 50)
    print()

    remove_codex_notify(codex_dir, dry_run)
    print()

    print("Note: Commands and scripts were kept.")
    print(f"      Delete {codex_dir / 'scripts'} manually if not needed.")
    print()

    if not dry_run:
        print("Restart Codex CLI for changes to take effect.")
    print()

    return True


# ---------------------------------------------------------------------------
# WSL re-launch helper
# ---------------------------------------------------------------------------


def _run_in_wsl(args: argparse.Namespace) -> int:
    """Re-execute this installer inside WSL so Path.home() resolves to the WSL home."""
    script_win = Path(__file__).resolve()
    # We need the repo-root install.py, not this module file.
    # Go up from installer/orchestration.py -> repo root / install.py
    install_py = script_win.parent.parent / "install.py"
    # Convert Windows path to WSL /mnt/ path
    drive = install_py.drive.rstrip(":").lower()
    posix_rest = install_py.as_posix().split(":", 1)[1]
    wsl_script = f"/mnt/{drive}{posix_rest}"

    cmd = ["wsl", "-e", "python3", wsl_script]
    if args.cli != "claude":
        cmd += ["--cli", args.cli]
    if args.dry_run:
        cmd.append("--dry-run")
    if args.uninstall:
        cmd.append("--uninstall")

    print("Re-launching installer inside WSL...")
    print(f"  wsl -e python3 {wsl_script}")
    print()
    result = subprocess.run(cmd)
    return result.returncode


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Install commands and notification hooks for Claude Code and/or Codex CLI"
    )
    parser.add_argument(
        "--cli",
        choices=["claude", "codex", "all"],
        default="claude",
        help="Which CLI to install for (default: claude)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without making them"
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove notification hooks (keeps commands/scripts)",
    )
    parser.add_argument(
        "--wsl",
        action="store_true",
        help="Install into WSL (re-runs installer inside WSL so paths resolve correctly)",
    )

    args = parser.parse_args()

    # WSL mode: re-execute inside WSL and exit
    if args.wsl:
        if not IS_WINDOWS:
            print("ERROR: --wsl flag is only needed when running from Windows.")
            print(
                "       You're already in a Linux/WSL environment -- run without --wsl."
            )
            sys.exit(1)
        sys.exit(_run_in_wsl(args))

    clis = ["claude", "codex"] if args.cli == "all" else [args.cli]
    success = True

    for cli in clis:
        if args.uninstall:
            if cli == "claude":
                success = uninstall(args.dry_run) and success
            else:
                success = uninstall_codex(args.dry_run) and success
        else:
            if cli == "claude":
                success = install(args.dry_run) and success
            else:
                success = install_codex(args.dry_run) and success

    sys.exit(0 if success else 1)
