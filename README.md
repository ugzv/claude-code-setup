# Claude Code Setup

Session tracking, commands, and notifications for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [Codex CLI](https://github.com/openai/codex).

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

By default this installs for Claude Code. To install for Codex CLI or both:

```bash
python install.py --cli codex   # Codex CLI only
python install.py --cli all     # Both CLIs
```

| | Claude Code | Codex CLI |
|---|---|---|
| Commands | `~/.claude/commands/` | `~/.codex/prompts/` |
| Settings | `~/.claude/settings.json` | `~/.codex/config.toml` |
| Project instructions | `CLAUDE.md` | `AGENTS.md` |
| SessionStart hook | Yes | Not yet supported |
| Statusline | Yes | Not yet supported |
| Notifications | Yes (Stop hook) | Yes (notify hook) |

Each CLI gets its own copy of scripts and independent runtime state (debounce, logs, toast identity).

### Setup a project

Restart your CLI, then in any project:

```
/migrate
```

Next session, the agent knows what you were working on.

### Upgrading existing projects

Run `/migrate` again — it's safe and non-destructive:
- Creates backups before any changes
- Preserves all existing data (state.json, backlog, shipped)
- Only adds missing features (handoff hooks, resume protocol)
- Custom CLAUDE.md/AGENTS.md content preserved

## The Problem

AI coding sessions are ephemeral. Context evaporates when a conversation ends. Next session starts from zero.

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

**`/dedup`** — Find duplicate code and plan consolidation
- `--aggressive` — Offer to implement top merge after report

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
├── CLAUDE.md              # Session protocol (Claude Code)
├── AGENTS.md              # Session protocol (Codex CLI)
└── .claude/
    ├── state.json         # Tracking data
    ├── settings.json      # Hook config
    ├── handoffs.json      # Active handoffs (if any)
    └── handoffs/          # Plan files (if any)
```

Global commands:
- Claude Code: `~/.claude/commands/`
- Codex CLI: `~/.codex/prompts/`

## Handoff System

For complex tasks that span sessions or need fresh context:

```
# Session 1: Analysis
/think [complex task]
/handoff

# Session 2: Execution (fresh context)
Agent: "1 active handoff: {task} (Phase 1/3). What would you like to work on?"
You: "continue"
# Agent reads plan, executes phase by phase, validates, captures learnings
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
- No rushing — the agent has abundant context

**Parallel sessions:**
- Multiple handoffs = multiple sessions OK (each works independently)
- Same handoff in multiple sessions = warned via `lastTouched` timestamp

**Non-intrusive:**
- Session start mentions handoffs but doesn't force engagement
- Say "continue" to resume, or do something else — handoffs wait

## Notifications

Desktop notifications when the agent finishes a task. Works with multiple instances—each notification shows which terminal/editor and project.

On macOS, the installer automatically installs `terminal-notifier` via Homebrew if available.

**Supported apps:** Cursor, VSCode, Windsurf, iTerm, Warp, Terminal, Windows Terminal, and more.

**Disable notifications:** Run `python install.py --uninstall` (or `--cli codex --uninstall` for Codex) to remove notification hooks while keeping commands.

## Statusline

Shows context usage at a glance (Claude Code only):

```
opus 4.6 │ main │ ●●●○○○○○○○  30%
```

## References

- [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
- [Codex CLI docs](https://github.com/openai/codex)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
