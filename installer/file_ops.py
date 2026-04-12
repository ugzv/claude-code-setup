"""File copy operations and install manifest for the installer."""

from dataclasses import dataclass
import re
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
    skip_if_exists: bool = False
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
    templates_step_number = 2 if cli == "claude" else 3
    scripts_step_number = 3 if cli == "claude" else 4

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
                    remove_obsolete=False,
                    missing_warning="Commands directory not found",
                ),
            ),
        ),
        InstallStep(
            number=templates_step_number,
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
            number=templates_step_number,
            title="Installing global CLAUDE.md...",
            summary_label="global defaults installed",
            operations=(
                CopySpec(
                    source_rel=("defaults", "CLAUDE.md"),
                    dest_parts=("CLAUDE.md",),
                    skip_if_exists=True,
                    missing_warning="Global CLAUDE.md template not found",
                ),
            ),
        ),
        InstallStep(
            number=scripts_step_number,
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


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
_DESCRIPTION_RE = re.compile(r'^description:\s*"?(.*?)"?\s*$', re.MULTILINE)
_CODEX_SKILL_PREFIX = "claude-code-setup-"
_CODEX_TRIGGER_HINTS = {
    "agent": (
        "Trigger when the user asks to audit a Claude Agent SDK project, review an "
        "agent architecture, inspect tool wiring, or assess an agent app design."
    ),
    "analyze": (
        "Trigger when the user asks for a codebase audit, architecture review, "
        "dependency review, naming review, comment review, technical debt scan, "
        "or history-based analysis."
    ),
    "backlog": (
        "Trigger when the user wants to review backlog items, triage follow-up work, "
        "capture technical debt, or decide what should be tracked for later."
    ),
    "commands": (
        "Trigger when the user asks what workflows are installed, which commands or "
        "skills are available, or how to invoke a setup workflow."
    ),
    "commit": (
        "Trigger when the user wants to commit changes, group work into clean commits, "
        "prepare a commit message, or commit and push the current session."
    ),
    "dedup": (
        "Trigger when the user asks to find duplicate code, repeated logic, copy-paste "
        "patterns, or consolidation opportunities."
    ),
    "dev": (
        "Trigger when the user wants to start, run, boot, restart, or relaunch a local "
        "development server, frontend server, backend server, UI, app, API, or both."
    ),
    "fix": (
        "Trigger when the user wants to fix lint errors, formatting issues, typecheck "
        "problems, broken quality checks, or clean up auto-fixable issues."
    ),
    "handoff": (
        "Trigger when the user wants to create a handoff, save progress for a fresh "
        "session, capture a phased plan, or package context for later execution."
    ),
    "health": (
        "Trigger when the user wants a project health check, repo sanity check, "
        "maintenance scan, or broad quality/status review."
    ),
    "migrate": (
        "Trigger when the user wants to set up session tracking, initialize project "
        "memory files, install project instructions, or migrate an existing repo."
    ),
    "prompt-guide": (
        "Trigger when the user asks for prompt-writing guidance, prompting philosophy, "
        "prompt review, or how to structure agent instructions."
    ),
    "push": (
        "Trigger when the user wants to push committed work, update session state, run "
        "final checks before pushing, or ship the current branch."
    ),
    "reflect": (
        "Trigger when the user wants a pre-mortem, risk review, regression review, "
        "change critique, or a pass over what might break."
    ),
    "test": (
        "Trigger when the user wants to run tests, rerun failing tests, start watch "
        "mode, validate the build, or verify the current changes."
    ),
    "think": (
        "Trigger when the user wants to think through a complex task, spec a solution, "
        "compare implementation options, or plan work before editing code."
    ),
    "ui": (
        "Trigger when the user wants a UI audit, visual consistency review, component "
        "quality review, or implementation quality pass for the interface."
    ),
    "ux": (
        "Trigger when the user wants a UX review, simulated user walkthrough, dead-end "
        "discovery, flow review, or usability critique."
    ),
}
_CODEX_EXAMPLE_REQUESTS = {
    "commit": (
        "Example requests: \"commit this session\", \"group and commit the changes\", "
        "\"commit and push what I just changed\"."
    ),
    "dev": (
        "Example requests: \"start frontend dev server\", \"run the backend locally\", "
        "\"boot the app\", \"restart both dev servers\"."
    ),
    "fix": (
        "Example requests: \"fix lint\", \"clean up formatting issues\", "
        "\"make the checks pass\"."
    ),
    "migrate": (
        "Example requests: \"set up this repo for future sessions\", "
        "\"initialize tracking here\", \"migrate this project\"."
    ),
    "prompt-guide": (
        "Example requests: \"help me write a better agent prompt\", "
        "\"review this system prompt\", \"what is a good prompting philosophy?\"."
    ),
    "push": (
        "Example requests: \"push this branch\", \"ship these commits\", "
        "\"run the push workflow\"."
    ),
    "test": (
        "Example requests: \"run the tests\", \"start test watch mode\", "
        "\"verify the suite passes\"."
    ),
    "think": (
        "Example requests: \"think through this refactor\", \"spec the approach first\", "
        "\"plan before coding\"."
    ),
}


def _load_command_metadata(command_file: Path) -> tuple[str, str]:
    """Return (description, body) from a command markdown file."""
    text = command_file.read_text(encoding="utf-8").replace("\r\n", "\n")
    match = _FRONTMATTER_RE.match(text)
    if match:
        frontmatter = match.group(1)
        body = text[match.end() :]
    else:
        frontmatter = ""
        body = text

    description_match = _DESCRIPTION_RE.search(frontmatter)
    description = description_match.group(1).strip() if description_match else ""

    body_lines = body.splitlines()
    while body_lines and body_lines[-1].strip() == "":
        body_lines.pop()
    if body_lines and body_lines[-1].strip() == "$ARGUMENTS":
        body_lines.pop()
    while body_lines and body_lines[-1].strip() == "":
        body_lines.pop()

    return description, "\n".join(body_lines).strip()


def _codex_skill_name(command_name: str) -> str:
    return f"{_CODEX_SKILL_PREFIX}{command_name}"


def _yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def _build_codex_skill_description(command_name: str, description: str) -> str:
    parts = [
        f"Use when the user wants the `/{command_name}` workflow.",
        description,
    ]
    trigger_hint = _CODEX_TRIGGER_HINTS.get(command_name)
    if trigger_hint:
        parts.append(trigger_hint)
    example_requests = _CODEX_EXAMPLE_REQUESTS.get(command_name)
    if example_requests:
        parts.append(example_requests)
    return " ".join(part for part in parts if part).strip()


def _render_codex_skill_md(command_name: str, description: str, body: str) -> str:
    skill_name = _codex_skill_name(command_name)
    skill_description = _build_codex_skill_description(command_name, description)
    parts = [
        "---",
        f"name: {_yaml_quote(skill_name)}",
        f"description: {_yaml_quote(skill_description)}",
        "---",
        "",
        f"# /{command_name} Skill",
        "",
        (
            "Use this skill for the Codex version of the "
            f"`/{command_name}` workflow from claude-code-setup."
        ),
        "",
        body,
        "",
    ]
    return "\n".join(parts)


def _render_codex_openai_yaml(command_name: str, description: str) -> str:
    skill_name = _codex_skill_name(command_name)
    default_prompt = (
        f"Use ${skill_name} when the user asks for /{command_name} or says things like "
        f"\"{command_name}\" in plain English. {description}"
    )
    return "\n".join(
        [
            "interface:",
            f"  display_name: {_yaml_quote(f'/{command_name}')}",
            f"  short_description: {_yaml_quote(description)}",
            f"  default_prompt: {_yaml_quote(default_prompt)}",
            "policy:",
            "  allow_implicit_invocation: true",
            "",
        ]
    )


def install_codex_skills(dry_run: bool = False) -> int:
    """Generate Codex skills from command markdown files."""
    repo_dir = get_repo_dir()
    source_dir = repo_dir / "commands"
    skills_dir = get_cli_dir("codex") / "skills"

    if not source_dir.exists():
        print(f"  WARNING: Commands directory not found: {source_dir}")
        return 0

    command_files = sorted(source_dir.glob("*.md"))
    expected_skill_names = {_codex_skill_name(path.stem) for path in command_files}

    if skills_dir.exists():
        for existing in skills_dir.iterdir():
            if not existing.is_dir():
                continue
            if existing.name.startswith(_CODEX_SKILL_PREFIX) and (
                existing.name not in expected_skill_names
            ):
                if dry_run:
                    print(f"  Would remove obsolete skill: {existing.name}")
                else:
                    shutil.rmtree(existing)
                    print(f"  Removed obsolete skill: {existing.name}")

    installed = 0
    for command_file in command_files:
        command_name = command_file.stem
        description, body = _load_command_metadata(command_file)
        skill_name = _codex_skill_name(command_name)
        skill_dir = skills_dir / skill_name
        agents_dir = skill_dir / "agents"
        skill_md = _render_codex_skill_md(command_name, description, body)
        openai_yaml = _render_codex_openai_yaml(command_name, description)

        if dry_run:
            print(f"  Would install skill: /{command_name} ({skill_name})")
        else:
            agents_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")
            (agents_dir / "openai.yaml").write_text(openai_yaml, encoding="utf-8")
        installed += 1

    return installed


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
    skip_if_exists: bool = False,
) -> bool:
    """Copy a single file, applying line-ending normalization when needed."""
    if not source_file.exists():
        return False

    if skip_if_exists and dest_file.exists():
        if dry_run:
            print(f"  Would keep existing: {dest_file.name}")
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
                    skip_if_exists=operation.skip_if_exists,
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
        remove_obsolete=False,
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
