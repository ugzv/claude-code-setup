# Claude Code Setup

Session tracking and commands for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Quick Start

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
| `/commit` | Commit with clean messages |
| `/push` | Push and update state |
| `/fix` | Auto-fix linting and formatting |
| `/test` | Run tests |

**Planning:**

| Command | Purpose |
|---------|---------|
| `/think` | Plan before complex tasks |
| `/backlog` | Review open items |
| `/prompt-guide` | Prompting philosophy for agent work |

**Setup & utilities:**

| Command | Purpose |
|---------|---------|
| `/migrate` | Set up tracking in a project |
| `/dev` | Start dev server (kills port first) |
| `/health` | Check project health |
| `/analyze` | Find code that resists change |
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

## Optional: Statusline

Shows context usage at a glance:

```
opus 4.5 │ main │ ●●●○○○○○○○  30%
```

## References

- [Claude Code docs](https://docs.anthropic.com/en/docs/claude-code)
- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
