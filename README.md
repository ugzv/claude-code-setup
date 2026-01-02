# Claude Code Setup

A tracking system and command library for [Claude Code][claude-code] that maintains context across sessions.

## The Problem

Claude sessions are ephemeral. When a conversation ends, context evaporates. The next session starts from zero.

## The Solution

A state file that persists across sessions:

```json
{
  "project": "my-app",
  "currentFocus": [{"description": "Implementing dark mode", "files": ["src/theme.ts"]}],
  "lastSession": {"date": "2025-12-17", "summary": "Fixed typing indicator bug"},
  "backlog": [{"description": "Refactor status constants", "type": "tech-debt"}],
  "shipped": [{"date": "2025-12-17", "type": "fix", "summary": "Typing indicator fix"}]
}
```

A SessionStart hook loads this automatically. Claude picks up where work left off.

## Installation

```bash
git clone https://github.com/ugzv/claude-code-setup.git
cd claude-code-setup
```

Then run the installer:

- macOS/Linux: `./install.sh`
- Windows: `install.bat`

Restart Claude Code. Run `/migrate` in any project to set up tracking.

## Commands

| Command | Purpose |
|---------|---------|
| `/migrate` | Set up tracking system in a project |
| `/think` | Plan approach before complex tasks |
| `/fix` | Auto-fix linting and formatting |
| `/test` | Run tests intelligently |
| `/commit` | Commit changes with clean messages |
| `/push` | Push and update state tracking |
| `/health` | Check project health (security, tests, deps) |
| `/analyze` | Find code that resists change |
| `/backlog` | Review and manage backlog items |
| `/agent` | Audit Claude Agent SDK projects |
| `/prompt-guide` | Load prompting philosophy for prompt work |
| `/commands` | List available project commands |

Commands use parallel subagents where beneficial. LSP integration is optional for more accurate code analysis in `/analyze` and `/think`.

## How It Works

1. Session starts, hook loads `state.json`
2. Claude has context from previous session
3. `/think` if task is complex
4. Work on the task
5. `/commit` with clean messages, capture discoveries
6. `/push` to remote, update state

## File Structure

After `/migrate`:

```
your-project/
├── CLAUDE.md              # Session protocol
└── .claude/
    ├── state.json         # Tracking data
    └── settings.json      # SessionStart hook
```

Global commands installed to `~/.claude/commands/`.

## Statusline

A minimal statusline shows context usage at a glance:

```
opus 4.5 │ main │ ●●●○○○○○○○  30%
```

- Model and git branch for orientation
- Visual progress bar for context window usage
- Color shifts: normal → white (60%) → yellow (75%) → red (90%)

Requires `jq` (`brew install jq` on macOS).

## Design Principles

**State as continuity.** Sessions end, but work continues. The state file bridges the gap.

**Verification over speculation.** Analysis commands require evidence. Claims without data are worthless.

**Philosophy over procedures.** Commands explain WHY, not step-by-step HOW. Claude reasons about the goal for each situation.

**Clean commits.** Atomic changes, clear messages, no AI fingerprints.

## Development

This repo is the source. Commands in `commands/*.md` get copied to `~/.claude/commands/` on install.

Run `./install.sh` after changes, then test in another project.

## References

- [Claude Code][claude-code] - Anthropic's agentic coding tool
- [Effective harnesses for long-running agents][harnesses] - Anthropic Engineering
- [Language Server Protocol][lsp] - LSP specification

[claude-code]: https://docs.anthropic.com/en/docs/claude-code
[harnesses]: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
[lsp]: https://microsoft.github.io/language-server-protocol/
