# Claude Code Setup

Session tracking, commands, and notifications for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

**Platforms:** macOS and Windows.

## Quick Start

Requires Python 3.8+.

```bash
git clone https://github.com/ugzv/claude-code-setup.git
cd claude-code-setup
./install.sh   # or install.bat on Windows
```

Restart Claude Code. In any project:

```
/migrate
```

Next session, Claude knows what you were working on.

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

**Daily workflow:**

| Command | Purpose |
|---------|---------|
| `/commit [--all\|--push]` | Commit changes. `--all` batches uncommitted, `--push` auto-pushes |
| `/push [--force]` | Push and update state. `--force` skips CI checks |
| `/fix` | Auto-fix linting and formatting |
| `/test [--watch]` | Run tests |
| `/reflect` | Pre-mortem analysis—find what will break before it does |

**Planning & analysis:**

| Command | Purpose |
|---------|---------|
| `/think` | Plan before complex tasks |
| `/backlog` | Review open items |
| `/analyze [mode]` | Codebase analysis. Modes: `--audit`, `--deps`, `--naming`, `--comments`, `--debt`, `--history` |
| `/prompt-guide` | Prompting philosophy for agent work |

**Setup & utilities:**

| Command | Purpose |
|---------|---------|
| `/migrate` | Set up tracking in a project |
| `/dev [--frontend\|--backend\|--all]` | Start dev server (kills port first) |
| `/health` | Check project health |
| `/ux` | Simulate users to find UX gaps and feature ideas |
| `/ui` | Audit visual consistency, detect "AI-generated look" issues |
| `/agent` | Audit Agent SDK projects |
| `/commands` | List available commands |

## File Structure

After `/migrate`:

```
your-project/
├── CLAUDE.md              # Session protocol
└── .claude/
    ├── state.json         # Tracking data
    └── settings.json      # Hook config
```

Global commands: `~/.claude/commands/`

## Notifications

Desktop notifications when Claude finishes a task. Works with multiple instances—each notification shows which terminal/editor and project.

On macOS, the installer automatically installs `terminal-notifier` via Homebrew if available.

**Supported apps:** Cursor, VSCode, Windsurf, iTerm, Warp, Terminal, Windows Terminal, and more.

**Disable notifications:** Run `python install.py --uninstall` to remove notification hooks while keeping commands.

## Statusline

Shows context usage at a glance:

```
opus 4.5 │ main │ ●●●○○○○○○○  30%
```

## References

- [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
