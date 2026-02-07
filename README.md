# Claude Code Setup

Session tracking, commands, and notifications for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

**Platforms:** macOS and Windows.

## Quick Start

### Prerequisites

**Python 3.8+** must be installed and available in your PATH. Hooks run Python scripts from any directory, so `python` (or `python3`) must work globally.

Verify with:

```bash
python --version   # or python3 --version on macOS/Linux
```

If this fails, install Python from [python.org](https://www.python.org/downloads/) and ensure "Add to PATH" is checked during installation.

### Install

```bash
git clone https://github.com/ugzv/claude-code-setup.git
cd claude-code-setup
./install.sh   # or install.bat on Windows
```

This copies commands to `~/.claude/commands/` and configures hooks in `~/.claude/settings.json`.

### Setup a project

Restart Claude Code, then in any project:

```
/migrate
```

Next session, Claude knows what you were working on.

### Upgrading existing projects

Run `/migrate` again — it's safe and non-destructive:
- Creates backups before any changes
- Preserves all existing data (state.json, backlog, shipped)
- Only adds missing features (handoff hooks, resume protocol)
- Custom CLAUDE.md content preserved

## The Problem

Claude sessions are ephemeral. Context evaporates when a conversation ends. Next session starts from zero.

## The Solution

A state file that persists:

```json
{
  "project": "my-app",
  "currentFocus": [{"description": "Implementing dark mode"}],
  "lastSession": {"date": "2025-12-17", "summary": "Fixed typing indicator bug"},
  "backlog": [{"summary": "Refactor status constants"}],
  "shipped": [{"date": "2025-12-17", "type": "fix", "summary": "Typing indicator fix"}]
}
```

A hook loads this on session start. `/push` trims `shipped` to 10 entries—older history lives in git.

## Commands

### Daily Workflow

**`/commit`** — Commit changes
- `--all` — Batch all uncommitted changes into logical commits
- `--push` — Auto-push after committing

**`/push`** — Push and update state.json
- `--force` — Skip CI checks

**`/fix`** — Auto-fix linting and formatting

**`/test`** — Run tests
- `--watch` — Watch mode

**`/reflect`** — Pre-mortem analysis (find what will break before it does)

### Planning & Analysis

**`/think`** — Plan before complex tasks
- `--gpt` — Get second opinion from GPT via Codex CLI

**`/handoff`** — Create handoff doc for fresh session to execute
- Captures analysis into phased plan
- Progress persists across sessions
- Self-validating phases

**`/backlog`** — Review and manage open items

**`/analyze`** — Codebase analysis
- `--audit` — Architecture review
- `--clarity` — Code clarity review
- `--deps` — Dependency analysis
- `--naming` — Naming consistency
- `--comments` — Comment quality
- `--debt` — Tech debt scan
- `--history` — Git history analysis

**`/prompt-guide`** — Prompting philosophy for agent work

### Setup & Utilities

**`/migrate`** — Set up tracking in a project

**`/dev`** — Start dev server (kills port first)
- `--frontend` — Frontend only
- `--backend` — Backend only
- `--all` — Both

**`/health`** — Check project health

**`/ux`** — Simulate users to find UX gaps

**`/ui`** — Audit visual consistency

**`/agent`** — Audit Agent SDK projects

**`/commands`** — List available commands

## File Structure

After `/migrate`:

```
your-project/
├── CLAUDE.md              # Session protocol
└── .claude/
    ├── state.json         # Tracking data
    ├── settings.json      # Hook config
    ├── handoffs.json      # Active handoffs (if any)
    └── handoffs/          # Plan files (if any)
```

Global commands: `~/.claude/commands/`

## Handoff System

For complex tasks that span sessions or need fresh context:

```
# Session 1: Analysis
/think [complex task]
/handoff

# Session 2: Execution (fresh context)
Claude: "1 active handoff: {task} (Phase 1/3). What would you like to work on?"
You: "continue"
# Claude reads plan, executes phase by phase, validates, captures learnings
```

**How it works:**
- `handoffs.json` tracks progress (machine-readable, updates as work happens)
- `handoffs/*.md` contain plans (human-readable, immutable after creation)
- Each phase has validation criteria
- `/push` auto-archives completed handoffs once code is committed

**Principles:**
- Plans are contracts — immutable once created
- Validate before marking complete — concrete evidence required
- Capture learnings — memory synthesis for future sessions
- No rushing — Claude has abundant context

**Parallel sessions:**
- Multiple handoffs = multiple sessions OK (each works independently)
- Same handoff in multiple sessions = warned via `lastTouched` timestamp

**Non-intrusive:**
- Session start mentions handoffs but doesn't force engagement
- Say "continue" to resume, or do something else — handoffs wait

## Notifications

Desktop notifications when Claude finishes a task. Works with multiple instances—each notification shows which terminal/editor and project.

On macOS, the installer automatically installs `terminal-notifier` via Homebrew if available.

**Supported apps:** Cursor, VSCode, Windsurf, iTerm, Warp, Terminal, Windows Terminal, and more.

**Disable notifications:** Run `python install.py --uninstall` to remove notification hooks while keeping commands.

## Statusline

Shows context usage at a glance:

```
opus 4.6 │ main │ ●●●○○○○○○○  30%
```

## References

- [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
