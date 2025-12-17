# Claude Code Setup

A tracking system for Claude Code that maintains context across sessions. Based on [Anthropic's best practices for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).

## What This Solves

- **Lost context** - Claude forgets what you were working on between sessions
- **No history** - No record of what was shipped or discovered
- **Stale backlogs** - Ideas and tech debt get lost or forgotten
- **Inconsistent commits** - Commit messages vary in quality

## How It Works

```
Session start (hook) → state.json loaded → Claude knows context
        ↓
      Work
        ↓
    /commit          → Clean commits during work
        ↓
     /push           → Push + update state + backlog check
```

**Single source of truth:** `.claude/state.json`

```json
{
  "project": "my-app",
  "currentFocus": "Implementing dark mode",
  "lastSession": {
    "date": "2025-12-17",
    "summary": "Fixed typing indicator bug",
    "commits": ["f3c149c"]
  },
  "backlog": [
    {
      "id": 1,
      "task": "Refactor status constants",
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

## Installation

### Quick Install

```bash
# Clone this repo
git clone https://github.com/ugzv/claude-code-setup.git

# Run install script
cd claude-code-setup
./install.sh
```

### Manual Install

```bash
# Create directories
mkdir -p ~/.claude/commands ~/.claude/templates

# Copy commands
cp commands/*.md ~/.claude/commands/

# Copy templates
cp templates/*.md ~/.claude/templates/
```

### Restart Claude Code

After installing, restart Claude Code to pick up the new commands.

## Usage

### For New Projects

```
/init-project
```

Creates:
- `CLAUDE.md` with session protocol at TOP
- `.claude/state.json`
- `.claude/settings.json` with SessionStart hook

### For Existing Projects

```
/migrate
```

Safely adds tracking to existing projects:
- Prepends session protocol to existing `CLAUDE.md`
- Creates backup before modifying
- Idempotent (safe to run multiple times)

### During Work

```
/commit
```

Clean commits with conventional format:
- No AI mentions or co-author tags
- Quality commit messages
- Only stages files you specify

### When Shipping

```
/push
```

Push and update tracking:
- Auto-detects resolved backlog items
- Updates `lastSession` and `shipped`
- Prompts for new backlog items
- Confirms `currentFocus` is still accurate

### Managing Backlog

```
/backlog         # Review all items
/backlog clean   # Remove old resolved items
```

## Commands Reference

| Command | Purpose |
|---------|---------|
| `/init-project` | Initialize new project with tracking |
| `/migrate` | Add tracking to existing project |
| `/commit` | Clean commit (no AI mentions) |
| `/push` | Push + update state + backlog check |
| `/backlog` | Review and manage backlog |

## File Structure

After setup, your project will have:

```
your-project/
├── CLAUDE.md                 # Session protocol at TOP
└── .claude/
    ├── state.json            # Single source of truth
    └── settings.json         # SessionStart hook
```

Global commands (in your home directory):

```
~/.claude/
├── commands/
│   ├── init-project.md
│   ├── migrate.md
│   ├── commit.md
│   ├── push.md
│   └── backlog.md
└── templates/
    └── CLAUDE.md
```

## How the Hook Works

The `SessionStart` hook in `.claude/settings.json` automatically reads `state.json` when:

- Claude Code starts
- You use `/resume`
- You use `/clear`
- Context compaction runs

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

## Ownership Rules

| Field | Who Sets It | When |
|-------|-------------|------|
| `currentFocus` | User only | User says "let's work on X" |
| `lastSession` | Claude | On `/push` |
| `backlog` | Claude adds, User removes | On `/push` |
| `shipped` | Claude | On `/push` |

## Backlog Lifecycle

```
Discovered during work
        ↓
      open
        ↓
   ┌────┴────┐
   ↓         ↓
resolved   wont-do
(auto on    (manual via
 /push)     /backlog)
```

## Credits

Inspired by [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) from Anthropic Engineering.
