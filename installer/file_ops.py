"""File copy operations for the installer.

Provides a generic copy_files() function and domain-specific wrappers for
commands, templates, scripts, and hooks.
"""

import shutil
import stat
from pathlib import Path

from .platform import IS_WINDOWS, get_claude_dir, get_repo_dir


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

    # On Linux/WSL, source files may come from a Windows mount (/mnt/c/...)
    # with CRLF line endings that break shebangs. Convert to LF for text files.
    fix_endings = not IS_WINDOWS and pattern in ("*.py", "*.sh", "*.md")

    # Copy files
    copied = 0
    for src_file in source_dir.glob(pattern):
        target = dest_dir / src_file.name
        if dry_run:
            print(f"  Would copy: {prefix}{src_file.name}")
        else:
            if fix_endings:
                content = src_file.read_bytes().replace(b"\r\n", b"\n")
                target.write_bytes(content)
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

    # Copy root-level Python scripts (remove_obsolete cleans up legacy scripts
    # like notify_completion.py that have been superseded by stop_hook.py)
    copied = copy_files(
        source_dir=source,
        dest_dir=dest,
        pattern="*.py",
        dry_run=dry_run,
        make_executable=True,
        remove_obsolete=True
    )

    # Copy lib/ subdirectory
    copied += _copy_lib_subdir(source, dest, dry_run)

    return copied



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
