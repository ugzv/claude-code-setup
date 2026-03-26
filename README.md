# Claude Code Setup

Session tracking, commands, and notifications for [Claude Code](https://code.claude.com/docs) and [Codex CLI](https://developers.openai.com/codex).

**Platforms:** macOS, Windows, and WSL.

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
python install.py --wsl         # Install into WSL from Windows
```

| | Claude Code | Codex CLI |
|---|---|---|
| Custom command/prompt files | `~/.claude/commands/` | `~/.codex/prompts/` |
| Settings | `~/.claude/settings.json` | `~/.codex/config.toml` |
| Project instructions | `CLAUDE.md` | `AGENTS.md` |
| SessionStart hook | Yes | Not yet supported |
| Statusline | Yes | Not yet supported |
| Notifications | Yes (Stop hook) | Yes (notify hook) |

Each CLI gets its own copy of scripts and independent runtime state (debounce, logs, toast identity).

Claude Code support here follows the documented `CLAUDE.md`, settings, hooks, and custom-command behavior. Codex CLI support follows the documented `AGENTS.md`, `config.toml`, and slash-command behavior.

The Codex-specific `~/.codex/prompts/` directory and top-level `notify` hook used by this repo are validated against the current CLI (`codex-cli 0.116.0`) and the shipped binary, but are not clearly documented on the public Codex docs site yet.

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

Claude Code loads this on `SessionStart`. Codex CLI uses the same project state files, but continuity comes from `AGENTS.md` and the installed prompts because SessionStart and statusline support are not available there yet. `/push` trims `shipped` to 10 entries; older history lives in git.

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
    ├── handoffs.json      # Active handoffs (if any)
    └── handoffs/          # Plan files (if any)
```

`~/.claude/settings.json` stays at user scope. A project-level `.claude/settings.json` is only for optional project overrides or legacy cleanup; `/migrate` should not create SessionStart hooks there.

Global custom command/prompt files:
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

The installer automatically handles platform dependencies:
- **macOS:** `terminal-notifier` and `jq` via Homebrew
- **WSL:** `jq` via apt-get; notifications use Windows balloon toasts via `powershell.exe`
- **Windows:** Uses native WinRT toast notifications

**Supported apps:** Cursor, VSCode, Windsurf, iTerm, Warp, Terminal, Windows Terminal, and more.

**Disable notifications:** Run `python install.py --uninstall` (or `--cli codex --uninstall` for Codex) to remove notification hooks while keeping commands.

## Statusline

Shows context usage at a glance (Claude Code only, requires `jq`):

```
opus │ main │ ●●●○○○○○○○  30%
```

## References

- [Claude Code memory (`CLAUDE.md`)](https://code.claude.com/docs/en/memory)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
- [Claude Code hooks](https://code.claude.com/docs/en/hooks)
- [Claude Code custom commands / skills](https://code.claude.com/docs/en/slash-commands)
- [Codex config basics (`~/.codex/config.toml`)](https://developers.openai.com/codex/config-basic)
- [Codex `AGENTS.md`](https://developers.openai.com/codex/guides/agents-md)
- [Codex slash commands](https://developers.openai.com/codex/cli/slash-commands)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
