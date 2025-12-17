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

### Batch Commit Everything

```
/commit-all
```

When you have multiple uncommitted changes (forgot to commit, multiple sessions, manual cleanup):
- Finds ALL uncommitted changes
- Groups related files together
- Creates separate commits for unrelated changes
- Shows plan and asks for confirmation
- Warns about sensitive files (.env, keys)

### Managing Backlog

```
/backlog         # Review all items
/backlog clean   # Remove old resolved items
```

### Code Analysis

```
/health      # Full project health check
/refactor    # Find refactoring opportunities
/unused      # Find dead code and unused deps
/todo-scan   # Find all TODO/FIXME markers
```

### Dependency Management

```
/deps        # Check outdated & vulnerable packages, update to latest
```

Uses security tools:
- **npm**: `npm audit`, `npm outdated`
- **Python**: `pip-audit`, `safety`, `deptry`
- **Rust**: `cargo audit`, `cargo outdated`

### Quick Context

```
/context     # Fast project orientation
```

Loads project state, structure, and recent activity in one command.

### Prompt Engineering

```
/prompt-audit   # Audit existing prompts for anti-patterns
/prompt-create  # Guide for writing new agent prompts
```

For building agentic applications. Based on philosophy-driven prompting principles:
- **Philosophy over rules** — Teach agents WHY, not just WHAT
- **Frameworks over examples** — Decision patterns, not lookup tables
- **Identity through beliefs** — Role prompting through values, not titles

## Commands Reference

### Setup Commands

| Command | Purpose |
|---------|---------|
| `/init-project` | Initialize new project with tracking |
| `/migrate` | Add tracking to existing project |

### Development Commands

| Command | Purpose |
|---------|---------|
| `/commit` | Clean commit (no AI mentions) |
| `/commit-all` | Commit ALL uncommitted changes, grouped intelligently |
| `/push` | Push + update state + backlog check |

### Analysis Commands

| Command | Purpose | Tools Used |
|---------|---------|------------|
| `/health` | Full project health check | tsc, eslint, pytest, cargo check |
| `/refactor` | Find code that needs refactoring | eslint, ruff, knip, clippy |
| `/unused` | Find unused code & dependencies | knip, vulture, depcheck, deptry |
| `/deps` | Update dependencies safely | npm audit, pip-audit, cargo audit |
| `/todo-scan` | Find TODO/FIXME/HACK markers | grep + git blame |

### Prompting Commands

| Command | Purpose |
|---------|---------|
| `/prompt-audit` | Audit prompts for anti-patterns (examples, lookup tables, procedures) |
| `/prompt-create` | Guide for writing new agent prompts with philosophy-driven approach |

### Context Commands

| Command | Purpose |
|---------|---------|
| `/context` | Quick project orientation |
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
│   ├── init-project.md    # Setup
│   ├── migrate.md
│   ├── commit.md          # Development
│   ├── commit-all.md
│   ├── push.md
│   ├── health.md          # Analysis
│   ├── refactor.md
│   ├── unused.md
│   ├── deps.md
│   ├── todo-scan.md
│   ├── prompt-audit.md    # Prompting
│   ├── prompt-create.md
│   ├── context.md         # Context
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

## What Gets Logged to Shipped

Only changes that affect behavior get logged:

| Type | Logged? | Reason |
|------|---------|--------|
| `feat` | Yes | New functionality |
| `fix` | Yes | Bug fix |
| `refactor` | Yes | Could break things, useful for debugging |
| `style` | No | Just formatting, no behavior change |
| `chore` | No | Cleanup, delete unused files |
| `docs` | No | Comments, README updates |

**Rule of thumb:** Does this change affect how the code behaves? If yes → log it. If no → skip.

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
