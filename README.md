# Claude Code Setup

A tracking system and command library for Claude Code that maintains context across sessions.

> **Note:** This is the **source repository** where the system is developed. After installation, these commands become available in all your projects to make Claude coding sessions more productive.

## The Problem

Claude sessions are ephemeral. When a conversation ends, everything learned about the project—what you were working on, what you discovered, what you shipped—evaporates. The next session starts from zero.

This creates real costs:
- Re-explaining context every session
- Lost discoveries and insights
- No continuity on multi-session work
- Inconsistent commit quality

## The Solution

State tracking creates continuity. A simple JSON file persists what matters:

```json
{
  "project": "my-app",
  "currentFocus": [
    {
      "description": "Implementing dark mode",
      "files": ["src/theme.ts", "src/components/Toggle.tsx"],
      "started": "2025-12-17"
    }
  ],
  "lastSession": {
    "date": "2025-12-17",
    "summary": "Fixed typing indicator bug",
    "commits": ["f3c149c"]
  },
  "backlog": [
    {
      "description": "Refactor status constants",
      "type": "tech-debt",
      "status": "open",
      "context": "Found while fixing indicator",
      "added": "2025-12-17"
    }
  ],
  "shipped": [
    {"date": "2025-12-17", "type": "fix", "summary": "Typing indicator fix"}
  ]
}
```

A SessionStart hook loads this automatically. The next Claude picks up where work left off.

## Philosophy-Driven Commands

These commands follow a core principle: **explain WHY, not just WHAT**.

Claude 4 follows instructions precisely. Show it examples, it matches them. Give it rules, it follows them mechanically. But explain the reasoning behind what you want, and it generalizes intelligently to novel situations.

Every command in this system teaches understanding rather than procedures. The result: commands that handle unexpected situations because they know the goal, not just the steps.

## Installation

```bash
git clone https://github.com/ugzv/claude-code-setup.git
cd claude-code-setup
./install.sh
```

Restart Claude Code to pick up the new commands.

## Quick Start

```
/migrate
```

Creates the tracking system: `CLAUDE.md` with session protocol, `.claude/state.json`, and the SessionStart hook. Safe to run on new or existing projects.

## Commands

### Development

| Command | What It Does |
|---------|--------------|
| `/fix` | Auto-fix all linting, formatting, unused imports. |
| `/test` | Run tests intelligently based on what's available. |
| `/commit` | Commit YOUR changes from this session. Clean messages, no AI fingerprints. |
| `/commit-all` | Commit ALL uncommitted changes, grouped by logical relationship. |
| `/push` | Push to remote, update state tracking. |

### Analysis

| Command | What It Does |
|---------|--------------|
| `/health` | Assess whether the team can ship with confidence. Includes TODO/FIXME scanning. |
| `/refactor` | Find code that resists change. Includes dead code and unused dependency detection. |
| `/deps` | Check security vulnerabilities and outdated packages. |

### Context

| Command | What It Does |
|---------|--------------|
| `/orient` | Quick project orientation—what is this, where are we, what's next. |
| `/backlog` | Review and manage backlog items. |
| `/commands` | List available project commands. |

### Prompting

| Command | What It Does |
|---------|--------------|
| `/prompt` | Load prompting philosophy, apply to any prompt work (create, audit, improve). |

### Setup

| Command | What It Does |
|---------|--------------|
| `/migrate` | Set up tracking system (works for new or existing projects). |

## How It Works

```
Session start → Hook loads state.json → Claude has context
                        ↓
                      Work
                        ↓
                    /commit → Clean commits, capture discoveries
                        ↓
                     /push → Push + update state + resolve backlog items
```

### The Hook

`.claude/settings.json` contains a SessionStart hook that fires on:
- Claude Code startup
- `/resume`
- `/clear`
- Context compaction

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat .claude/state.json 2>/dev/null || echo '{\"note\": \"No state.json found.\"}'"
          }
        ]
      }
    ]
  }
}
```

### Parallel Sessions

`currentFocus` is an array, supporting multiple Claude sessions working on different parts of the same project. Each session registers what files it's touching, enabling conflict detection.

## File Structure

After setup:

```
your-project/
├── CLAUDE.md              # Session protocol at top
└── .claude/
    ├── state.json         # Tracking data
    └── settings.json      # SessionStart hook
```

Global commands:

```
~/.claude/
└── commands/
    ├── fix.md
    ├── test.md
    ├── commit.md
    ├── commit-all.md
    ├── push.md
    ├── health.md
    ├── refactor.md
    ├── deps.md
    ├── orient.md
    ├── backlog.md
    ├── commands.md
    ├── prompt.md
    └── migrate.md
```

## Design Principles

**State as continuity.** Sessions end, but work continues. The state file bridges the gap.

**Verification over speculation.** Analysis commands like `/refactor` require evidence. "This file changes frequently" needs git history to back it up. Claims without data are worthless.

**Philosophy over procedures.** Commands explain WHY something matters, not step-by-step HOW. Claude reasons about the goal and figures out the approach for each situation.

**Clean commits as communication.** Commits are for humans reading history months later. Atomic changes, clear messages, no AI fingerprints.

**Backlog as persistent memory.** Discoveries made while working get captured before context evaporates. Future sessions can act on them.

## Development

This repo is the source for the command system. To work on it:

```bash
cd claude-code-setup
```

**Key files:**
- `.claude/commands/*.md` - Command source files (copied to `~/.claude/commands/` on install)
- `install.sh` - Installation script
- `CLAUDE.md` - Instructions for Claude when working on THIS project

**When adding/modifying commands, consider:**
- Would this help during actual coding sessions?
- Is it used frequently enough to justify existing?
- Could it be consolidated with another command?
- Does it explain WHY (philosophy) not just WHAT (procedures)?

**Testing changes:**
Run `./install.sh` to copy updated commands to `~/.claude/commands/`, then test in another project.

## Credits

Inspired by [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) from Anthropic Engineering.

Prompt philosophy based on [Claude 4 best practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices).
