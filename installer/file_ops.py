"""File copy operations and install manifest for the installer."""

from dataclasses import dataclass
import shutil
import stat
from pathlib import Path
from .platform import IS_WINDOWS, get_cli_dir, get_claude_dir, get_repo_dir


@dataclass(frozen=True)
class CopySpec:
    """One copy operation within an install step."""

    source_rel: tuple[str, ...]
    dest_parts: tuple[str, ...]
    pattern: str | None = None
    make_executable: bool = False
    remove_obsolete: bool = False
    prefix: str = ""
    missing_warning: str | None = None


@dataclass(frozen=True)
class InstallStep:
    """Declarative install step for a CLI target."""

    number: int
    title: str
    summary_label: str | None
    operations: tuple[CopySpec, ...]


def _cli_home(cli: str) -> Path:
    return get_claude_dir() if cli == "claude" else get_cli_dir(cli)


def _build_install_steps(cli: str) -> tuple[InstallStep, ...]:
    commands_subdir = "commands" if cli == "claude" else "prompts"

    steps = [
        InstallStep(
            number=1,
            title="Installing commands...",
            summary_label="commands installed",
            operations=(
                CopySpec(
                    source_rel=("commands",),
                    dest_parts=(commands_subdir,),
                    pattern="*.md",
                    remove_obsolete=True,
                    missing_warning="Commands directory not found",
                ),
            ),
        ),
        InstallStep(
            number=2,
            title="Installing templates...",
            summary_label="templates installed",
            operations=(
                CopySpec(
                    source_rel=("templates",),
                    dest_parts=("templates",),
                    pattern="*.md",
                ),
            ),
        ),
        InstallStep(
            number=3,
            title="Installing notification scripts...",
            summary_label="scripts installed",
            operations=(
                CopySpec(
                    source_rel=("scripts",),
                    dest_parts=("scripts",),
                    pattern="*.py",
                    make_executable=True,
                    remove_obsolete=True,
                    missing_warning="Scripts directory not found",
                ),
                CopySpec(
                    source_rel=("scripts", "lib"),
                    dest_parts=("scripts", "lib"),
                    pattern="*.py",
                    prefix="lib/",
                ),
            ),
        ),
    ]

    if cli == "claude":
        steps.append(
            InstallStep(
                number=5,
                title="Installing hooks...",
                summary_label="hooks installed",
                operations=(
                    CopySpec(
                        source_rel=("hooks",),
                        dest_parts=("hooks",),
                        pattern="*.py",
                        make_executable=True,
                    ),
                ),
            )
        )

    return tuple(steps)


def copy_files(
    source_dir: Path,
    dest_dir: Path,
    pattern: str,
    dry_run: bool = False,
    make_executable: bool = False,
    remove_obsolete: bool = False,
    prefix: str = "",
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
                target.chmod(
                    target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )
        copied += 1

    return copied


def copy_file(
    source_file: Path,
    dest_file: Path,
    dry_run: bool = False,
    make_executable: bool = False,
) -> bool:
    """Copy a single file, applying line-ending normalization when needed."""
    if not source_file.exists():
        return False

    if dry_run:
        print(f"  Would copy: {source_file.name}")
        return True

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    fix_endings = not IS_WINDOWS and source_file.suffix in (".py", ".sh", ".md")

    if fix_endings:
        dest_file.write_bytes(source_file.read_bytes().replace(b"\r\n", b"\n"))
    else:
        shutil.copy2(source_file, dest_file)

    if make_executable and not IS_WINDOWS:
        dest_file.chmod(
            dest_file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        )

    return True


def run_install_steps(
    cli: str,
    dry_run: bool = False,
    only_steps: tuple[int, ...] | None = None,
) -> dict[str, int]:
    """Execute the declarative install plan for a CLI target."""
    repo_dir = get_repo_dir()
    cli_home = _cli_home(cli)
    results: dict[str, int] = {}

    for step in _build_install_steps(cli):
        if only_steps is not None and step.number not in only_steps:
            continue
        print(f"Step {step.number}: {step.title}")
        step_count = 0

        for operation in step.operations:
            source_path = repo_dir.joinpath(*operation.source_rel)
            dest_path = cli_home.joinpath(*operation.dest_parts)

            if operation.pattern is None:
                if not source_path.exists():
                    if operation.missing_warning:
                        print(f"  WARNING: {operation.missing_warning}")
                    continue
                copied = copy_file(
                    source_path,
                    dest_path,
                    dry_run=dry_run,
                    make_executable=operation.make_executable,
                )
                step_count += int(copied)
                continue

            if not source_path.exists():
                if operation.missing_warning:
                    print(f"  WARNING: {operation.missing_warning}: {source_path}")
                continue

            step_count += copy_files(
                source_dir=source_path,
                dest_dir=dest_path,
                pattern=operation.pattern,
                dry_run=dry_run,
                make_executable=operation.make_executable,
                remove_obsolete=operation.remove_obsolete,
                prefix=operation.prefix,
            )

        if step.summary_label and not dry_run:
            print(f"  {step_count} {step.summary_label}")
        print()
        results[step.title] = step_count

    return results


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
        prefix="lib/",
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
        remove_obsolete=True,
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
        remove_obsolete=False,
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
        remove_obsolete=True,
    )

    # Copy lib/ subdirectory
    copied += _copy_lib_subdir(source, dest, dry_run)

    return copied


def copy_statusline(dry_run: bool = False) -> bool:
    """Legacy helper retained for compatibility; statusline now ships as scripts/statusline.py."""
    repo_dir = get_repo_dir()
    source = repo_dir / "statusline.sh"
    dest = get_claude_dir() / "statusline.sh"

    if not source.exists():
        print("  WARNING: statusline.sh not found")
        return False

    if dry_run:
        print("  Would copy: statusline.sh")
    else:
        if not IS_WINDOWS:
            # Fix CRLF from Windows mounts
            dest.write_bytes(source.read_bytes().replace(b"\r\n", b"\n"))
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
        remove_obsolete=False,
    )
